from __future__ import division
import pandas as pd
import os
import math
from pylab import *
from multiprocessing import Pool

__author__ = 'Vladimir Iglovikov'


p = Pool(2)
data_path = os.path.join("..", 'data')

trip = pd.read_csv(os.path.join(data_path, "train", "drivers", "1", '1.csv' ))

#TODO
def derivative(x_list, y_list):
    result = []
    for x in range(2, len(x_list) - 2):
        result += [(-y_list[x + 2] + 8 * y_list[x + 1] - 8 * y_list[x - 1] + y_list[x - 2]) / 12]
    return x_list[2:-2], result

def telematics(driver_path, trip_path):
    '''

    :param trip:
    :return: dataframe with rows pathlength, trip time
    '''
    trip = pd.read_csv(os.path.join(data_path, "train", "drivers", driver_path, trip_path))
    x_list = trip['x'].values
    y_list = trip['y'].values
    trip_time = len(trip.index)
    path = 0
    not_moving = 0

    t_list = range(trip_time)

    tx, v_x = derivative(t_list, x_list)
    tx, v_y = derivative(t_list, y_list)

    ttx, a_x = derivative(tx, v_x)
    ttx, a_y = derivative(tx, v_y)

    list_v = []

    for t in range(1, len(tx)):
        v = math.sqrt((v_x[t] - v_x[t-1])**2 + (v_y[t] - v_y[t-1])**2)
        list_v += [v]

    list_a = []

    for t in range(1, len(ttx)):
        a = math.sqrt((a_x[t] - a_x[t-1])**2 + (a_y[t] - a_y[t-1])**2)
        list_a += [a]


    for t in range(1, trip_time):
        dL = math.sqrt((y_list[t] - y_list[t-1])**2 + (x_list[t] - x_list[t-1])**2)
        path += dL
        if dL == 0:
            not_moving += 1

    average_speed = path / trip_time
    result = pd.DataFrame()
    result["driver_trip"] = [driver_path + "_" + trip_path.replace(".csv", "")]
    result["driver"] = [int(driver_path)]
    result["trip"] = [int(trip_path.replace(".csv", ""))]
    result['pathlength'] = [path]
    result['triptime'] = [trip_time]
    result['average_speed'] = [average_speed]
    result['not_moving'] = [not_moving]
    result['percent_not_moving'] = [not_moving / trip_time]

    list_v = map(abs, list_v)

    result['average_momentarily_speed'] = [np.mean(list_v)]
    result['max_speed'] = [max(list_v)]
    result['min_speed'] = [min(list_v)]

    list_a = map(abs, list_a)
    result['average_acceleration'] = [np.mean(list_a)]
    result['max_acceleration'] = [max(list_a)]
    result['min_acceleration'] = [min(list_a)]

    return result


print 'create tidy for training'

driver_list = os.listdir(os.path.join(data_path, "train", "drivers"))

x = len(driver_list)

ind = 0
for driver in driver_list:
    result = []
    print
    print driver
    print ind / x

    trip_list = os.listdir(os.path.join(data_path, "train", "drivers", driver))

    for trip in trip_list:
        temp = telematics(driver, trip)
        result += [temp]
    ind += 1

    result_data = pd.concat(result)

    result_data = result_data.sort(["driver", "trip"])
    result_data.to_csv(os.path.join(data_path, "training", driver + ".csv"), index=False)