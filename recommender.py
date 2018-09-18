# Below are the python modules we would be using.
import numpy as np
import pandas as pd
import os, glob, sys , re
import sklearn , pickle
from datetime import datetime

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
import datetime
import preprocess , postprocess , path

import path

# Environment Variables
# Below are the various locations where we look for various files, which have the data required by the bot

# Utility Functions
# Utility Methods that are required. Below is a short description of what it does & why is it needed.

def train():
    # Pre-process Data
    print('Started train')
    sm9_data_with_RITM, sm9_data_without_RITM = preprocess.getSM9TrainData(os.path.join(path.DIR_NAME , path.SM9_TRAINING_DATA))
    sn_data = preprocess.getServiceNowTrainData(os.path.join(path.DIR_NAME , path.SERVICE_NOW_TRAINING_DATA))
    merged_data_with_cat_item, merged_data_without_cat_item = preprocess.mergeTrainingData(sm9_data_with_RITM, sn_data)
    sm9_data_without_RITM, merged_data_without_cat_item = preprocess.prepareDataByRBCTitle(sm9_data_without_RITM,merged_data_without_cat_item)
    #     sm9_data_without_RITM = sm9_data_without_RITM[['RBC Line Item Title','Assigned to']]
    #     merged_data_without_cat_item = merged_data_without_cat_item[['RBC Line Item Title','Assigned to']]
    tickets_by_title = pd.concat([sm9_data_without_RITM, merged_data_without_cat_item])

    clf_by_cat_item = trainModel(merged_data_with_cat_item['cat_item'], merged_data_with_cat_item['Assigned to'],
                                 os.path.join(path.DIR_NAME , path.CAT_ITEM_MODEL),
                                 os.path.join(path.DIR_NAME , path.COUNT_VEC_CAT_ITEM))
    clf_by_title = trainModel(tickets_by_title['RBC Line Item Title'], tickets_by_title['Assigned to'],
                              os.path.join(path.DIR_NAME , path.RBC_TITLE_MODEL),
                              os.path.join(path.DIR_NAME , path.COUNT_VEC_BY_TITLE))
    print('Ended train')


#     return tickets_by_title
# train models & save them




def predict():
    # Pre-process Data
    print('Started predict')
    sm9_data_with_RITM, sm9_data_without_RITM = preprocess.getSM9TestData(os.path.join(path.DIR_NAME , path.SM9_TEST_DATA))
    sn_data = preprocess.getServiceNowTestData(os.path.join(path.DIR_NAME , path.SERVICE_NOW_TEST_DATA))
    merged_data_with_cat_item, merged_data_without_cat_item = preprocess.mergeTestData(sm9_data_with_RITM, sn_data)
    sm9_data_without_RITM, merged_data_without_cat_item = preprocess.prepareDataByRBCTitle(sm9_data_without_RITM, merged_data_without_cat_item)
    #     sm9_data_without_RITM = sm9_data_without_RITM[['RBC Line Item Title']]
    #     merged_data_without_cat_item = merged_data_without_cat_item[['RBC Line Item Title']]
    tickets_by_title = pd.concat([sm9_data_without_RITM, merged_data_without_cat_item])
    sorted_analyst_prob_by_item = predictModelByCatItem(merged_data_with_cat_item['cat_item'],
                                                        os.path.join(path.DIR_NAME , path.CAT_ITEM_MODEL),
                                                        os.path.join(path.DIR_NAME , path.COUNT_VEC_CAT_ITEM))
    cat_item_ticket_recommendations = postprocess.postProcess(sorted_analyst_prob_by_item, merged_data_with_cat_item)
    sorted_analyst_prob_by_title = predictModelByTitle(tickets_by_title['RBC Line Item Title'],
                                                       os.path.join(path.DIR_NAME , path.RBC_TITLE_MODEL),
                                                       os.path.join(path.DIR_NAME , path.COUNT_VEC_BY_TITLE))
    rbc_title_ticket_recommendations = postprocess.postProcess(sorted_analyst_prob_by_title, tickets_by_title)
    ticket_recommendations = pd.concat([cat_item_ticket_recommendations, rbc_title_ticket_recommendations])
    recommendations = "tickets_recommendations_" + datetime.datetime.today().strftime('%Y-%m-%d') + ".xlsx"
    filename = os.path.join(path.DIR_NAME , path.RECOMMENDATIONS_DIR , recommendations)
    #     filename = "tickets_recommendation_" + datetime.datetime.now().isoformat() + ".xlsx"
    # Prefarably save as excel
    # ticket_recommendations.to_csv(path_or_buf=filename  , encoding="Latin-1" , index = False)
    # ticket_recommendations.to_excel(path_or_buf=filename , index = False)
    # Save as excel
    writer = pd.ExcelWriter(filename, engine='xlsxwriter')
    ticket_recommendations.to_excel(writer,'Sheet1', index=False)
    writer.save()
    print('Ended predict')
    # Done saving recommendations as excel.
    # Send email to email list.


#     os.environ['SERVICE_NOW_TRAINING_DATA'] = "rawdata\\serviceNow\\train\\*.csv"
#     os.environ['SERVICE_NOW_TEST_DATA'] = "rawdata\\serviceNow\\test\\*.csv"
# Load Models & pass data
# Post-process recommendations



# Train

# features : X ; labels : Y ; filename : model name ; location : where model is stored.
# Try using joblib to persist the model.
def trainModel(features , labels, model , countVec):
    print('Started trainModel')
    print('features : ', features)
    cv = CountVectorizer(ngram_range=(2, 2) , stop_words='english')
    X = cv.fit_transform(features)
    Y = labels
    #len(cv.get_feature_names())
    # Removed stratify=Y as the least populated class has only 1 sample.
    # X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.03, random_state=42)
    #print(X_train.shape , Y_train.shape , X_test.shape , Y_test.shape)
    clf = MultinomialNB()
    clf = MultinomialNB().fit(X, Y)
    # save the model to disk
    pickle.dump(clf, open(model, 'wb'))
    # save count vectorizer to disk
    pickle.dump(cv, open(countVec, 'wb'))
    # predict_proba = clf.predict_proba(X_test)
    print('Ended trainModel')
    return clf

## Predict

# TO-DO : Use joblib to load the model
def predictModelByCatItem(features, model, countVec):
    # Code to preprocess the data
    # Code to load the model
    print('Started predictModelByCatItem')
    print("features : ", features.shape)
    cv = pickle.load(open(countVec, 'rb'))
    clf = pickle.load(open(model, 'rb'))

    # cv = CountVectorizer(ngram_range=(2, 2) , stop_words='english')
    # cv = CountVectorizer(ngram_range=(2, 2) )
    X = cv.transform(features)

    predict_proba = clf.predict_proba(X)
    analyst_prob = []
    for p_p in predict_proba:
        analyst_prob.append(zip(clf.classes_, p_p))
    sorted_analyst_prob = []
    for lpp in analyst_prob:
        sorted_analyst_prob.append(sorted(lpp, key=lambda x: x[1], reverse=True))
    print('Ended predictModelByCatItem')
    return sorted_analyst_prob
    # Code for model evaluation. Not relevant at this point
    #     index_match = []
    #     for i,slp in enumerate(sorted_analyst_prob) :
    #         index_match.append([lb[0] for lb in slp].index(Y_test.iloc[i]))
    #     index_match


# TO-DO : Use joblib to load the model
def predictModelByTitle(features, model, countVec):
    # Code to preprocess the data
    # Code to load the model
    print('Started predictModelByTitle')
    print("features : ", features.shape)
    cv = pickle.load(open(countVec, 'rb'))
    clf = pickle.load(open(model, 'rb'))

    # cv = CountVectorizer(ngram_range=(2, 2) , stop_words='english')
    X = cv.transform(features)
    # clf = pickle.load(open(filename_location, 'rb'))
    predict_proba = clf.predict_proba(X)
    analyst_prob = []
    for p_p in predict_proba:
        analyst_prob.append(zip(clf.classes_, p_p))
    sorted_analyst_prob = []
    for lpp in analyst_prob:
        sorted_analyst_prob.append(sorted(lpp, key=lambda x: x[1], reverse=True))
    print('Started predictModelByTitle')
    return sorted_analyst_prob
    # Code for model evaluation. Not relevant at this point
    #     index_match = []
    #     for i,slp in enumerate(sorted_analyst_prob) :
    #         index_match.append([lb[0] for lb in slp].index(Y_test.iloc[i]))
    #     index_match

