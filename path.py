# Contains all relative paths with respect to our project.
import os
DIR_NAME = os.path.dirname(__file__)
APP_ROOT = os.path.dirname(os.path.abspath(''))
ESAM_OPS_ROASTER = 'data/postprocess/team/Team List.xlsx'
TEAMS = 'data/postprocess/global/Global 2018 Operations Schedule.xlsx'
CLIENT_BASE_MAPPER = 'data/postprocess/client_base_mapper/Client_Base_to_Team_Mapper.xlsx'
VACATION_SCHEDULE = 'data/postprocess/vc/Vacation Calendar 2018.xlsx'
OPEN_TICKETS_PER_ANALYST = 'data/postprocess/otpa/otpa.xlsx'

SM9_TRAINING_DATA = 'data/sm9/train/*.xlsx'
SM9_TEST_DATA = 'data/sm9/test/*.xlsx'
SERVICE_NOW_TRAINING_DATA = 'data/serviceNow/train/*.xlsx'
SERVICE_NOW_TEST_DATA = 'data/serviceNow/test/*.xlsx'
RECOMMENDATIONS_DIR = 'data/recommendations/'

CAT_ITEM_MODEL = 'models/by_cat_item.pkl'
COUNT_VEC_CAT_ITEM = 'models/count_vec_cat_item.pkl'

RBC_TITLE_MODEL = 'models/by_title.pkl'
COUNT_VEC_BY_TITLE = 'models/count_vec_by_title.pkl'
