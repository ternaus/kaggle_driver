#!/usr/bin/env python
from __future__ import division
__author__ = 'Vladimir Iglovikov'

#initialize libraries

import os
import pandas as pd
from sklearn.cluster import KMeans
from multiprocessing import Pool
import random
import time
from sklearn.svm import OneClassSVM
from sklearn import mixture

random.seed(666)
p = Pool(3)

def classify(driver_data):
    '''

    It is assumed that most of the trips belong to the same driver

    :param driver: driver that we need to analyze
    :return: data frame that will tell probability that his trip belongs to this particular driver
    '''

    # gmm = mixture.GMM(n_components=2)
    gmm = mixture.VBGMM(n_components=2)
    # gmm = KMeans(n_clusters=2)
    # cv = OneClassSVM()
    data = driver_data.drop(["driver_trip",
                             "driver",
                             "trip",
                             "average_speed",
                             "not_moving",
                             "percent_not_moving",
                             "average_momentarily_speed",
                             "min_speed",
                             "average_acceleration",
                             # "max_acceleration",
                             "min_acceleration"], axis=1)
    # cv.fit(data)

    # predictions = cv.predict(data)
    predictions = gmm.fit(data).predict(data)

    # predictions = (predictions + 1) / 2

    if sum(predictions) / 200 < 0.5: #Here I hardcode that we have 200 trips per driver
        predictions = map(lambda x: 1 - x, predictions)

    result = pd.DataFrame()
    result["driver_trip"] = driver_data["driver_trip"]
    result["prob"] = predictions
    return result

def get_df(driver):
    return pd.read_csv(os.path.join("..", "data", "training", str(driver)))


data_to_work_with = map(get_df, os.listdir(os.path.join("..", "data", "training")))

print "create list of data frames with predictions"
result = map(classify, data_to_work_with)
print "concatenate data"
final_result = pd.concat(result)
print "done with predictions"

final_result.to_csv(os.path.join("..", "data", "submission_{timestamp}".format(timestamp=time.time())), index=False)