import csv
import datetime
import glob
import json
import time
from os import listdir
from os.path import isfile, join
import redis
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
import matplotlib


base_path = '/home/ridl/rajibs_work/advanced_pema/workload_module/sock_shop/log_data/vertical_and_horizontal/catalogue_x1_c0.5/'
log_path = base_path + 'rps_200_profile_0/logs'


def load_data_files():
    onlyfiles = [f for f in listdir(log_path) if isfile(join(log_path, f))]
    # print(onlyfiles)
    dataframes = []
    for f in onlyfiles:
        temp = pd.read_csv(log_path + "/" + f, parse_dates=["arrival_time"],
                           index_col="arrival_time")
        dataframes.append(temp)
    return dataframes


def load_data_files_without_index(file_path):
    onlyfiles = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    # print(onlyfiles)
    dataframes = []
    for f in onlyfiles:
        temp = pd.read_csv(file_path + "/" + f)
        dataframes.append(temp)
    return dataframes


def merge_requests():
    rps_list = ['100', '200', '300', '400', '500', '600', '700', '800']

    rps_list = ['400']
    profiles = [str(x) for x in range(4)]
    # profiles = ['3']
    slot_id = 1
    for rps in rps_list:
        for profile in profiles:
            experiment_name = 'rps_' + rps + '_iteration_' + profile
            iteration_path = base_path + experiment_name + '/'
            file_path = iteration_path + "logs"

            data_files = load_data_files_without_index(file_path)
            final_df = pd.DataFrame()
            # request_counts = []
            for i in range(len(data_files)):
                temp = data_files[i]
                # request_counts.append(len(temp.index))
                final_df = pd.concat([final_df, temp])
            # print(final_df)
            # sort the dataframe by request arrival time
            final_df = final_df.sort_values(by='arrival_time')
            # print(final_df)
            # drop some columns
            final_df = final_df.drop(['service', 'status_code', 'user'], axis=1)

            # get size of total rows
            size_of_df = len(final_df.index)

            # create request id for each requests
            request_ids = [i + 1 for i in range(size_of_df)]
            slot_ids = [slot_id for _ in range(size_of_df)]

            final_df['slot_id'] = slot_ids
            final_df['request_id'] = request_ids
            final_df.to_csv(iteration_path + experiment_name + '.csv', index=False,
                            columns=['slot_id', 'request_id', 'arrival_time', 'response_time', 'latency'])
            print("RPS is ", size_of_df / 120.0)
            print("Latency is: ", final_df.latency.quantile(0.99) * 1000)
            print("Done for ", experiment_name)
            slot_id += 1
    # print(final_df.head())

merge_requests()