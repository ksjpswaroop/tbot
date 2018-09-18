# Post-process Recommendations
import pandas as pd
import utility , app , path
import preprocess , os
from datetime import datetime
from dateutil import relativedelta

# import os
# dirname = os.path.dirname(__file__)

### Teams

def test_postprocess():
    print('APP_ROOT : ',app.APP_ROOT)
# These are teams we have in ESAM that work on tickets

def getTeams():
    print('Started getTeams')
    from datetime import datetime
    #analyst_teams = pd.read_excel(os.environ['PROJECT_DIR'] +  '\\rawdata\\Global 2018 Operations Schedule.xlsx', sheetname='MONTHLY SCHEDULE', header = 2 , index_col=0)
    file_name = os.path.join(path.DIR_NAME , path.TEAMS)
    analyst_teams = pd.read_excel( file_name ,sheetname='MONTHLY SCHEDULE', header=2, index_col=0)
    team_name = []
    team_index = analyst_teams.index.tolist()
    for t in team_index:
        if type(t) is str:
            team_name.append(t)
    # Get the month for which we want the team for .
    current_month = datetime.now().strftime('%B') # 'August'
    team_dict = {} # Dictionary of team name as key & team mates as value.
    for t in range(len(team_name) - 1):
        team = analyst_teams.loc[team_name[t]:team_name[t+1] , current_month]
        team = team.iloc[:len(team) - 1]
        team.reset_index(drop=True,inplace=True)
        team = team.loc[~team.isnull()]
        team = team[:len(team)]
        team_dict[team_name[t]] = team
    print('Ended getTeams')
    return team_dict

### Client Base to Teams Mapping

def getClientBaseToTeamMapping():
    print('Started getClientBaseToTeamMapping')
    #client_base_to_team = pd.read_excel(os.environ['PROJECT_DIR'] +  '\\rawdata\\Client_Base_to_Team_Mapper.xlsx',index_col=0)
    client_base_to_team_file_path = os.path.join(path.DIR_NAME , path.CLIENT_BASE_MAPPER)
    client_base_to_team = pd.read_excel(client_base_to_team_file_path ,index_col=0)
    print('Ended getClientBaseToTeamMapping')
    return client_base_to_team

### Vacation Schedule

# Get Vacation Schedule: Returns the vacation calender for current month.
# Used to filter out analyst on leave.

def getVacationSchedule():
    print('Started getVacationSchedule')
    #all_vacation = pd.read_excel(os.environ['PROJECT_DIR'] +  '\\rawdata\\Vacation Calendar 2018.xlsx', sheetname='All', index_col=0)
    vacation_schedule_file_path = os.path.join(path.DIR_NAME , path.VACATION_SCHEDULE)
    print('vacation_schedule_file_path : ' , vacation_schedule_file_path)
    all_vacation = pd.read_excel(vacation_schedule_file_path, sheetname='All',index_col=0)
    all_vacation.columns = list(range(1,32))
    # Get the month & year. This would be used to get vacation information for the corresponding month and year.
    current_month = datetime.now().strftime('%B') # 'August'
    current_year = datetime.now().strftime('%Y')  # 2018
    month_year = (current_month + ' ' + str(current_year)).upper()
    next_month_year = ''
    vc = pd.DataFrame()
    # Make sure the year in the below condition is a variable. What if the year is December 2019. Then the below code would fail.
    if month_year != 'DECEMBER 2018':
        #nextmonth = datetime.date.today() + relativedelta.relativedelta(months=1)
        nextmonth = datetime.now() + relativedelta.relativedelta(months=1)
        next_month = nextmonth.strftime('%B')
        next_month_year = (next_month + ' ' + current_year).upper()
        vc = all_vacation.loc[month_year : next_month_year]
    else:
        # What if the month year is December 2018
        # In this case you would use the current month_year variable.
        vc = all_vacation.loc[month_year : ]
        pass
    #print("To : " , next_month_year)
    print('Ended getVacationSchedule')
    return vc

vc = getVacationSchedule()

# Code to check if an analyst is on vacation

# Based on current day & the analyst name, check if the analyst is on a vacation.

def isAnalystOnLeave(analyst_name):
    #     print('Started isAnalystOnLeave')
    from datetime import datetime
    leave_days = [7.5, 7.50, 'L', 'C', 'T']
    current_day = int(datetime.now().strftime('%d'))
    try:
        if vc.loc[analyst_name][current_day] in leave_days:
            # print("Yes")
            #             print('Ended isAnalystOnLeave : True')
            print(analyst_name + ' is on leave. No tickets would be assigned.')
            return True
        else:
            #             print('Ended isAnalystOnLeave : False')
            return False
    except Exception as e:
        # print("Exceptin in isAnalystOnLeave : " , e)
        return False

### Availability

# Get all tickets in an analyst's queue.
# Some files use csv , where as others use .xlsx . Lets standardize to excel sheets as they occupy less space. Check & ensure
# the same applies on the linux box too
def getAvailabilityPerAnalyst():
    print('Started getAvailabilityPerAnalyst')
    availability_columns = ['Assigned to','Pending Customer','Client Base']
    #availability = pd.read_csv(os.environ['PROJECT_DIR'] +  '\\rawdata\\availability.csv' , encoding='latin-1' , usecols=availability_columns )
    #availability = pd.read_excel(os.environ['PROJECT_DIR'] +  '\\rawdata\\availability.xlsx' , usecols=availability_columns )
    tickets_assigned_file_path = os.path.join(path.DIR_NAME, path.OPEN_TICKETS_PER_ANALYST)
    availability = pd.read_excel(tickets_assigned_file_path)
    availability = availability[availability_columns]
    availability = availability.loc[~availability['Assigned to'].isnull()]
    availability['Pending Customer'] = availability['Pending Customer'].fillna('FALSE')
    availability['Assigned to'] = availability['Assigned to'].apply(utility.object_to_int)
    availability_grouped = availability.groupby(['Assigned to','Pending Customer']).count()
    availability_grouped.rename(columns = {'Client Base' : 'No_of_Tickets_Assigned'} , inplace=True)
    team_sheet_without_leads = utility.getAnalyst()
    analyst_emp_id = team_sheet_without_leads.index.tolist()
    tickets_analyst_queue = {}
    for analyst in analyst_emp_id:
        try:
            tickets_analyst_queue[analyst] = availability_grouped.loc[(analyst,'FALSE')]['No_of_Tickets_Assigned']
        except Exception as e:
            print("Exception in getAvailabilityPerAnalyst : " , e)
            tickets_analyst_queue[analyst] = 0
    print('Availability')
    print(tickets_analyst_queue)
    print('Ended getAvailabilityPerAnalyst')
    return tickets_analyst_queue


#team_sheet_without_leads = utility.getAnalyst()

def postProcess(sorted_analyst_prob, ticket):
    # This variable will save a list of recommendations for each ticket
    print('Started postProcess')
    r1, r2, r3, r4 = [], [], [], []
    recommendations_list = []
    client_base_to_team = getClientBaseToTeamMapping()
    team_dict = getTeams()
    tickets_analyst_queue = getAvailabilityPerAnalyst()
    count = 0
    for index, t in ticket.iterrows():
        #         print("t  " , t)
        #         print("t['Client Base'] :  ", t['Client Base'])
        c_b = t['Client Base']
        #         print("c_b : ", c_b)
        #         print("type(c_b) : ", type(c_b))
        # TO-DO What if the client base is null
        # if c_b != np.nan:
        if pd.isnull(c_b):
            t_l = ['All']
        else:
            team = client_base_to_team.loc[c_b, 'ESAM Application Teams ']
            t_l = team.split('|')
        # Get me all the analyst to be considered for this ticket
        a_l = []
        if t_l[0] in 'All':
            #a_l = team_sheet_without_leads['Name'].tolist()
            a_l = utility.team_sheet_without_leads['Name'].tolist()
            # Consider all analyst across all teams
            # iterate through all keys of team_list dictionary. Set a_l to the list of analyst across teams.
        else:
            for team in t_l:
                team = team.strip()
                for t_m in team_dict[team]:
                    a_l.append(t_m)
                    # We now have all analyst we need to consider.
                    #             print(a_l)
        # Check Vacation Calender & remove those on Vacation
        # Use List comprehension insead of the below line
        analyst_not_on_vacation = []
        for a in a_l:
            if isAnalystOnLeave(a):
                continue
            else:
                analyst_not_on_vacation.append(a)
        # analyst_not_on_vacation
        # Getting employee id based on analyst name.
        analyst_not_on_leave = []
        # Below line is commented as we made team_sheet_without_leads global
        # team_sheet_without_leads = getAnalyst()
        for a in analyst_not_on_vacation:
            try:
                emp_id = (
                    utility.team_sheet_without_leads.loc[utility.team_sheet_without_leads['Name'].str.strip() == a.strip()]).index.tolist()[0]
                analyst_not_on_leave.append(emp_id)
            except Exception as e:
                print("Exception in postprocess while looping over analyst_not_on_vacation", e)
                print("a :", a)
                #                 print("team_dict : ", team_dict)
                #                 print("team_sheet_without_leads : ",team_sheet_without_leads)
                # print(emp_id)

        # analyst_not_on_leave
        # Get probability of analyst to be considered , sort them in descending order. It already sorted. Evaluate your approach
        # Do you need to iterate through it OR you can pick the analyst. Some thought needed.
        analyst_prob = []
        for i in range(len(sorted_analyst_prob[count])):
            if sorted_analyst_prob[count][i][0] in analyst_not_on_leave:
                analyst_prob.append(sorted_analyst_prob[count][i])
        # analyst_prob
        # Check availability & don't consider analyst having more than 45 tickets. Need to amend this later to give lower probability to
        # those having more tickets in their bin. Once you have 4 analyst who can resolve such tickets & are available.
        analyst_avail = {}
        for a in analyst_prob:
            try:
                analyst_avail[a[0]] = tickets_analyst_queue[a[0]]
            except Exception as e:
                print("Exception in postprocess while looping over analyst_prob ", e)
                analyst_avail[a[0]] = -1
                # tickets_analyst_queue
        # analyst_avail
        recommendations = []
        for a_p in analyst_prob:
            if analyst_avail[a_p[0]] <= 45:
                recommendations.append(utility.team_sheet_without_leads.loc[a_p[0]]['Name'])
        recommendations_list.append(recommendations)
        count = count + 1

    # Add recommendations to the tickets
    print('Size of Recommendations_list : ', len(recommendations_list))
    print('Number of tickets in shape : ', ticket.shape)
    for r in recommendations_list:
        try:
            r1.append(r[0])
        except Exception as e:
            r1.append('None 1')
            print("r1.append(r[0]) : ", e)
        try:
            r2.append(r[1])
        except Exception as e:
            r2.append('None 2')
            print("r2.append(r[1]) : ", e)
        try:
            r3.append(r[2])
        except Exception as e:
            r3.append('None 3')
            print("r3.append(r[2]) : ", e)
        try:
            r4.append(r[3])
        except Exception as e:
            r4.append('None 4')
            print("r3.append(r[3]) : ", e)

    R1 = pd.Series(r1, index=ticket.index)
    R2 = pd.Series(r2, index=ticket.index)
    R3 = pd.Series(r3, index=ticket.index)
    R4 = pd.Series(r4, index=ticket.index)
    #     print('R4 : ', R4)

    ticket['R1'] = R1
    ticket['R2'] = R2
    ticket['R3'] = R3
    ticket['R4'] = R4
    print('Ended postProcess')
    return ticket

