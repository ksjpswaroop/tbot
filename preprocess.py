import pandas as pd
import glob , os
import utility , path


def getSM9TrainData(location):
    #sm9_files = glob.glob(os.environ['PROJECT_DIR'] +  location)
    print('Started getSM9TrainData')
    sm9_files = glob.glob(location)
    print('sm9_files : ', sm9_files)
    sm9_columns = ['Assigned Dept', 'Assigned to', 'Number','RBC Line Item Title', 'RBCMMPRITM', 'Rbc Description', 'Client Base']
    # Read tickets in CSV file
    #sm9_data_list = [ pd.read_csv(sm9_file , encoding='latin-1' ) for sm9_file in sm9_files ]
    # Read tickets in Excel file
    sm9_data_list = [ pd.read_excel(sm9_file) for sm9_file in sm9_files ]
    sm9_data = pd.concat(sm9_data_list)
    sm9_data = sm9_data[sm9_columns]
    sm9_data = sm9_data.reset_index(drop=True)
    print('sm9_data test : ', sm9_data.columns)
    print('sm9_data.head() : ', sm9_data.head())
    #print('sm9_data : Before preprocessing ' , sm9_data)
    #sm9_data.head()
    # Consider only Windows & Application tickets
    sm9_data = sm9_data.loc[sm9_data['Assigned Dept'].isin(['EAA_WINDOWS SERVICES_IMPL' , 'EAA_APPLICATION SERVICES_IMPL'])]
    print('sm9_data 1 : ', sm9_data.shape)
    # Remove those tickets that don't have Analyst linked to it. Noise.
    sm9_data = sm9_data[pd.notnull(sm9_data['Assigned to'])]
    print('sm9_data 2 : ', sm9_data.shape)
    # Convert objects (float values in particular) to int
    sm9_data['Assigned to'] = sm9_data['Assigned to'].apply(utility.object_to_int)
    # Give me only those tickets, who are assigned to analyst who are part of the current team.
    team_sheet_without_leads = utility.getAnalyst()
    print('team_sheet_without_leads 1 : ', team_sheet_without_leads.shape)
    analyst_emp_id = team_sheet_without_leads.index.tolist()
    #print('analyst_emp_id : ', analyst_emp_id)
    sm9_data = sm9_data.loc[sm9_data['Assigned to'].isin(analyst_emp_id)]
    print('sm9_data 3 : ', sm9_data.shape)
    # Set client base as Windows for tickets that have null Client Base & Assigned Dept as EAA_WINDOWS SERVICES_IMPL
#     win_tickets_null_client_base = sm9_data.loc[(sm9_data['Client Base'].isnull()) & (sm9_data['Assigned Dept'] == 'EAA_WINDOWS SERVICES_IMPL')].index.tolist()
#     sm9_data.loc[win_tickets_null_client_base , 'Client Base'] = 'Windows'
    # If RBC Line Item Title is null , then set replace it with RBC Description.
    tickets_with_no_title = sm9_data.loc[sm9_data['RBC Line Item Title'].isnull()].index.tolist()
    sm9_data.loc[tickets_with_no_title,'RBC Line Item Title'] = sm9_data.loc[tickets_with_no_title,'Rbc Description']
    sm9_data_without_RITM = sm9_data.loc[sm9_data['RBCMMPRITM'].isnull()]
    sm9_data_with_RITM = sm9_data.loc[~sm9_data['RBCMMPRITM'].isnull()]
    # print('sm9_data_with_RITM : ', sm9_data_with_RITM)
    # print('sm9_data_with_RITM : ', sm9_data_with_RITM)
    print('sm9_data_without_RITM.shape : ', sm9_data_without_RITM.shape)
    print('Done getSM9TrainData')
    return sm9_data_with_RITM , sm9_data_without_RITM


def getSM9TestData(location):
    #sm9_files = glob.glob(os.environ['PROJECT_DIR'] +  location)
    print('Started getSM9TestData')
    sm9_files = glob.glob(location)
    sm9_columns = ['Assigned Dept', 'Number','RBC Line Item Title', 'RBCMMPRITM', 'Rbc Description', 'Client Base']
    #sm9_data_list = [ pd.read_csv(sm9_file , encoding='latin-1' , usecols=sm9_columns ) for sm9_file in sm9_files ]
    # Read tickets in CSV file
    #sm9_data_list = [ pd.read_csv(sm9_file , encoding='latin-1' ) for sm9_file in sm9_files ]
    # Read tickets in Excel file
    sm9_data_list = [ pd.read_excel(sm9_file) for sm9_file in sm9_files ]
    sm9_data = pd.concat(sm9_data_list)
    sm9_data = sm9_data[sm9_columns]
    sm9_data = sm9_data.reset_index(drop=True)
    #sm9_data.head()
    # Consider only Windows & Application tickets
    sm9_data = sm9_data.loc[sm9_data['Assigned Dept'].isin(['EAA_WINDOWS SERVICES_IMPL' , 'EAA_APPLICATION SERVICES_IMPL'])]
    # If you need files for training then 'Assigned To' can't be null. However, if you're giving recommendations,
    # then Assigned To would be null
    # Remove those tickets that don't have Analyst linked to it. Noise.
    #sm9_data = sm9_data[pd.notnull(sm9_data['Assigned to'])]
    # Convert objects (float values in particular) to int
    #sm9_data['Assigned to'] = sm9_data['Assigned to'].apply(object_to_int)
    # Give me only those tickets, who are assigned to analyst who are part of the current team.
    #analyst_emp_id = getAnalyst().index.tolist()
    #sm9_data = sm9_data.loc[sm9_data['Assigned to'].isin(analyst_emp_id)]
    # Set client base as Windows for tickets that have null Client Base & Assigned Dept as EAA_WINDOWS SERVICES_IMPL
    win_tickets_null_client_base = sm9_data.loc[(sm9_data['Client Base'].isnull()) & (sm9_data['Assigned Dept'] == 'EAA_WINDOWS SERVICES_IMPL')].index.tolist()
    sm9_data.loc[win_tickets_null_client_base , 'Client Base'] = 'Windows'
    # If RBC Line Item Title is null , then set replace it with RBC Description.
    tickets_with_no_title = sm9_data.loc[sm9_data['RBC Line Item Title'].isnull()].index.tolist()
    sm9_data.loc[tickets_with_no_title,'RBC Line Item Title'] = sm9_data.loc[tickets_with_no_title,'Rbc Description']
    sm9_data_without_RITM = sm9_data.loc[sm9_data['RBCMMPRITM'].isnull()]
    #23672
    sm9_data_with_RITM = sm9_data.loc[~sm9_data['RBCMMPRITM'].isnull()]
    #159162
    print('Ended getSM9TestData')
    return sm9_data_with_RITM , sm9_data_without_RITM


# clean RBC Line Item Title
# try to pass a parameter only the column you are updating rather than the dataframe

def cleanTicketTitle(data):
    print('Started cleanTicketTitle')
    data['RBC Line Item Title'] = data['RBC Line Item Title'].str.replace(r"\d+/\d+",'')
    data['RBC Line Item Title'] = data['RBC Line Item Title'].str.replace(r"[0-9]",'')
    #sm9_data_without_RITM['RBC Line Item Title'] = sm9_data_without_RITM['RBC Line Item Title'].str.replace(r"[0-9]",'')
    data['RBC Line Item Title'] = data['RBC Line Item Title'].str.replace(r"A termination request has recently been submitted on behalf of RBC Access Manager for .*",'termination request Access Manager')
    data['RBC Line Item Title'] = data['RBC Line Item Title'].str.replace(r"Access Manager manual termination request submitted .*",'Access Manager manual termination')
    data['RBC Line Item Title'] = data['RBC Line Item Title'].str.replace(r"An access review has recently been completed .*",'access review completed')
    data['RBC Line Item Title'] = data['RBC Line Item Title'].str.replace(r'[:.,-/?*[\]&+()!]',' ')
    data['RBC Line Item Title'] = data['RBC Line Item Title'].str.replace(r'( ESC | PA | PO | PC | PD| Apr | April )','')
    data['RBC Line Item Title'] = data['RBC Line Item Title'].str.replace(r'  ',' ')
    data['RBC Line Item Title'] = data['RBC Line Item Title'].str.strip()
    print('Ended cleanTicketTitle')
    return data


## Service Now

# Need to pass it a parameter to recognize whether we're dealing with training or test data.
def getServiceNowTrainData(location):
    print('Started getServiceNowTrainData')
    #sn_files = glob.glob(os.environ['PROJECT_DIR'] +  location)
    print("Service Now Training Files Location : ", location)
    sn_files = glob.glob(location)
    print("sn_files : " , sn_files)
    #sn_files
 #   sn_columns = ['cat_item' , 'number' , 'u_assignment_group', 'state' , 'stage' ]
    sn_columns = ['cat_item', 'number', 'u_assignment_group']
#     reqd_stages = ['Fulfillment']
#     reqd_states = ['Work in Progress','Open']
    #sn_df = [pd.read_csv(sn_file , encoding='latin-1' , usecols=sn_columns) for sn_file in sn_files]
    # , usecols = sn_columns
    sn_df = [pd.read_excel(sn_file) for sn_file in sn_files]

    sn_data = pd.concat(sn_df)

    print("sn_data.columns : ", sn_data.columns)
    print("sn_data.head() ", sn_data.head())
    sn_data = sn_data[sn_columns]
    print(sn_data.head())
    sn_data = sn_data.loc[sn_data['u_assignment_group'].isin(['EAA_WINDOWS SERVICES_IMPL','EAA_APPLICATION SERVICES_IMPL'])]
    #sn_data = sn_data.loc[sn_data['state'].str.strip().isin(reqd_states) | sn_data['stage'].str.strip().isin(reqd_stages)]
    print('Ended getServiceNowTrainData')
    return sn_data
    #sn_data.head()

def getServiceNowTestData(location):
    print('Started getServiceNowTestData')
    sn_files = glob.glob(location)
    print('sn_files : ', sn_files)
    #sn_files
    sn_columns = ['cat_item' , 'number' , 'u_assignment_group', 'state' , 'stage' ]
    reqd_stages = ['Fulfillment']
    reqd_states = ['Work in Progress','Open']
    #sn_df = [pd.read_csv(sn_file , encoding='latin-1' , usecols=sn_columns) for sn_file in sn_files]
    sn_df = [pd.read_excel(sn_file) for sn_file in sn_files]
    sn_data = pd.concat(sn_df)
    print('sn_data : ' , sn_data.head())
    sn_data = sn_data[sn_columns]
    print('sn_data.columns : ', sn_data.columns)
    sn_data = sn_data.loc[sn_data['u_assignment_group'].isin(['EAA_WINDOWS SERVICES_IMPL','EAA_APPLICATION SERVICES_IMPL'])]
    sn_data = sn_data.loc[sn_data['state'].str.strip().isin(reqd_states) | sn_data['stage'].str.strip().isin(reqd_stages)]
    print("sn_data.shape : ", sn_data.shape)
    print('Ended getServiceNowTestData')
    return sn_data
    #sn_data.head()


### Merge Data


def mergeTrainingData(sm9_data_with_RITM, sn_data):
    #     sm9_data_with_RITM , sm9_data_without_RITM = getSM9TrainData()
    #     sn_data = getServiceNowTrainData()
    print('Started mergeTrainingData')
    merged_data = pd.merge(sn_data, sm9_data_with_RITM, left_on='number', right_on='RBCMMPRITM', how='outer',indicator=True)
    # Only consider tickets assigned to analyst. Remove tickets that are auto-completed.
    merged_data = merged_data.loc[~merged_data['Assigned to'].isnull()]
    # Convert Assigned to from float to int.
    merged_data['Assigned to'] = merged_data['Assigned to'].apply(utility.object_to_int)
    # You might need RBC Description for cases when RBC Line Item Title is null.
    # merged_data = merged_data[
    #     ['number', 'Number', 'cat_item', 'u_assignment_group', 'Assigned to', 'RBC Line Item Title', 'Rbc Description',
    #      'Client Base', 'state', 'stage']]
    merged_data = merged_data[
        ['number', 'Number', 'cat_item', 'u_assignment_group', 'Assigned to', 'RBC Line Item Title', 'Rbc Description',
         'Client Base']]
    merged_data_without_cat_item = merged_data.loc[merged_data['cat_item'].isnull()]
    merged_data_with_cat_item = merged_data.loc[~merged_data['cat_item'].isnull()]

    # merged_data_by_title = mergeDataByRBCTitle(sm9_data_without_RITM,merged_data_without_cat_item)
    print('Ended mergeTrainingData')
    return merged_data_with_cat_item, merged_data_without_cat_item


def mergeTestData(sm9_data_with_RITM, sn_data):
    #     sm9_data_with_RITM , sm9_data_without_RITM = getSM9TrainData()
    #     sn_data = getServiceNowTrainData()
    print('Started mergeTestData')
    merged_data = pd.merge(sn_data, sm9_data_with_RITM, left_on='number', right_on='RBCMMPRITM', how='outer',
                           indicator=True)
    # Only consider tickets assigned to analyst. Remove tickets that are auto-completed.
    # merged_data = merged_data.loc[~merged_data['Assigned to'].isnull()]
    # Convert Assigned to from float to int.
    # merged_data['Assigned to'] = merged_data['Assigned to'].apply(object_to_int)
    # You might need RBC Description for cases when RBC Line Item Title is null.
    merged_data = merged_data[
        ['Assigned Dept', 'number', 'Number', 'cat_item', 'u_assignment_group', 'RBC Line Item Title',
         'Rbc Description', 'Client Base', 'state', 'stage']]
    merged_data_without_cat_item = merged_data.loc[merged_data['cat_item'].isnull()]
    merged_data_with_cat_item = merged_data.loc[~merged_data['cat_item'].isnull()]
    # merged_data_by_title = mergeDataByRBCTitle(sm9_data_without_RITM,merged_data_without_cat_item)

    # Set client base as Windows for tickets that have null Client Base & Assigned Dept as EAA_WINDOWS SERVICES_IMPL
    win_tickets_null_client_base = merged_data_with_cat_item.loc[
        (merged_data_with_cat_item['Client Base'].str.strip().isnull()) & (
        (merged_data_with_cat_item['Assigned Dept'].str.strip() == 'EAA_WINDOWS SERVICES_IMPL') | (
        merged_data_with_cat_item['u_assignment_group'].str.strip() == 'EAA_WINDOWS SERVICES_IMPL'))].index.tolist()
    merged_data_with_cat_item.loc[win_tickets_null_client_base, 'Client Base'] = 'Windows'

    # Set client base as Windows for tickets that have null Client Base & Assigned Dept as EAA_WINDOWS SERVICES_IMPL
    win_tickets_null_client_base = merged_data_without_cat_item.loc[
        (merged_data_without_cat_item['Client Base'].str.strip().isnull()) & (
        (merged_data_without_cat_item['Assigned Dept'].str.strip() == 'EAA_WINDOWS SERVICES_IMPL') | (
        merged_data_with_cat_item['u_assignment_group'].str.strip() == 'EAA_WINDOWS SERVICES_IMPL'))].index.tolist()
    merged_data_without_cat_item.loc[win_tickets_null_client_base, 'Client Base'] = 'Windows'

    print('merged_data_with_cat_item : ', merged_data_with_cat_item.shape)
    print('merged_data_without_cat_item : ', merged_data_without_cat_item.shape)
    print('Ended mergeTestData')
    return merged_data_with_cat_item, merged_data_without_cat_item


def prepareDataByRBCTitle(sm9_data_without_RITM ,merged_data_without_cat_item):
    print('Started prepareDataByRBCTitle')
    sm9_data_without_RITM = cleanTicketTitle(sm9_data_without_RITM)
    merged_data_without_cat_item = cleanTicketTitle(merged_data_without_cat_item)
    print('Ended prepareDataByRBCTitle')
    return sm9_data_without_RITM , merged_data_without_cat_item


