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

plt.rcParams.update({'pdf.fonttype': 42})
plt.rcParams.update({"font.size": 40})
plt.rcParams.update({"font.weight": 'bold'})

base_path = '/home/ridl/rajibs_work/advanced_pema/workload_module/log_data/hr_data/vertical_horizontal/'
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
    rps_list = ['200', '250', '300', '350', '400', '450', '500', '550', '600']
    profiles = [str(x) for x in range(3)]
    settings = ['4', '5']

    final_results = []

    for setting in settings:
        for rps in rps_list:
            for profile in profiles:
                experiment_name = 'rps_' + rps + '_iteration_' + profile
                iteration_path = base_path + "settings_" + setting + "/" + experiment_name + '/'
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
                final_rps = size_of_df / 120.0
                latency = final_df.latency.quantile(0.99) * 1000
                final_results.append(['settings_' + setting, final_rps, latency])
                # print("Done for ", experiment_name)

    with open(base_path + 'response_times_with_settings.csv', 'w') as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(['settings', 'RPS', 'Latency'])
        csvwriter.writerows(final_results)


merge_requests()
