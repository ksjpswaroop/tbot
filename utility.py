import pandas as pd
import os
import path

# object_to_int : Used when model is pre-processed. Converts float (.0) & NaN's to integer for Analyst Employee Id. Analyst Id's
# are numbers , not floating point. If number is not an integer, we're presently setting to an arbitrary value. Such values would
# be removed later as we only consider analyst that are part of the team & have been assigned tickets.
# import os
# dirname = os.path.dirname(__file__)

def object_to_int(x):
    try:
        return int(x)
    except ValueError:
        return 123

# getAnalyst : Gives all the analyst we have in ESAM Operations as per the 'Team List.xlsx' file. We remove FTE Team Lead, as they
# don't work on tickets. This method returns employee id's as an index , along with analyst's name, skills  & status. We'll
# refer to this as ESAM Operations Roastor, to avoid mixing it with the various internal teams (e.g : Windows, Insurance etc)
# we have.

def getAnalyst():
    #team_data_columns = ['Name','Status','Employee #','Windows & Appliciation (Line of Business) Skillset']
    team_data_columns = ['Name', 'Status',  'Windows & Appliciation (Line of Business) Skillset']

    print("dirname : ", path.DIR_NAME)
    print('path.APP_ROOT : ', path.APP_ROOT)
    print('path.ESAM_OPS_ROASTER : ', path.ESAM_OPS_ROASTER)
    file_path = os.path.join(path.DIR_NAME , path.ESAM_OPS_ROASTER)
    print("file_path : ", file_path)
    # header=1 ,  index_col = 2 , usecols = team_data_columns
    team_sheet = pd.read_excel(file_path , engine = 'xlrd'  , index_col=2 )
   # print('teamsheet.index : ', team_sheet.index)
    team_sheet = team_sheet[team_data_columns]
    #team_sheet = pd.read_excel(dirname + path.ESAM_OPS_ROASTER, header=1, index_col=2)

    #print("team_sheet.columns : " , team_sheet.columns)
    #team_sheet = team_sheet[team_data_columns]
    print(team_sheet.head())
    team_sheet_without_leads = team_sheet.loc[team_sheet['Status'] != 'FTE Team Lead']
    analyst_emp_id = team_sheet_without_leads.index.tolist()
    return team_sheet_without_leads

team_sheet_without_leads = getAnalyst()