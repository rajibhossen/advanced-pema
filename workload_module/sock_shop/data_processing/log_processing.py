import glob
import json
from os import listdir
from os.path import isfile, join

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

base_path = 'log_data/early_detection/'


def load_data_files(file_path, flag):
    """
    load csv files as panda dataframes
    :return: list
    """
    # logpath = base_path + str(file_path)
    onlyfiles = [f for f in listdir(file_path) if isfile(join(file_path, f))]
    #print(onlyfiles)
    dataframes = []
    for f in onlyfiles:
        # if f.endswith(".txt"):
        #     continue
        temp = pd.read_csv(file_path + "/" + f, parse_dates=["arrival_time"],
                           index_col="arrival_time")
        dataframes.append(temp)
    #print(dataframes)
    return dataframes


def end_to_end(log_path, duration=120.0, percentile=99):
    rpss = []
    avgs = []
    percentiles = []

    #p = str(profile) + "/" + str(experiment_no)
    x = []
    responses = []

    data_files = load_data_files(file_path=log_path, flag=False)
    for temp in data_files:
        df = temp
        df1 = df.groupby("user")["response_time"].agg(["count", "sum"])

        for a in df1["sum"].values:
            responses.append(a)

        x.append(df1["count"].sum())

    # print(responses)
    rpss.append(sum(x) / duration)
    # avgs.append((sum(responses) / len(responses)) * 1000)
    percentile_response = np.percentile(np.array(responses), percentile)
    percentiles.append(percentile_response * 1000)

    #xs, ys, zs = rpss, avgs, percentiles
    #print(xs, zs)
    return rpss, percentiles


def end_to_end_values(log_path):
    responses = []

    data_files = load_data_files(file_path=log_path,flag=False)
    final_df = pd.DataFrame()
    request_counts = []
    for i in range(len(data_files)):
        temp = data_files[i]
        request_counts.append(len(temp.index))
        final_df = pd.concat([final_df, temp])

    for index, row in final_df.iterrows():
        responses.append(row['response_time'])
    return sum(request_counts), responses


def process_utlization(profile):
    experiment_no = 1
    path = base_path + str(profile) + "_" + str(experiment_no)
    txt_file = glob.glob(path + '/*.txt')
    utils = {}
    throttles = {}
    js_file = open(txt_file[0])
    data = json.load(js_file)
    for row in data:
        for key in row:
            if key in utils:
                utils[key].append(row[key]["cpu_util_avg_percent"])
                throttles[key].append(row[key]["cpu_throttle"])
            else:
                utils[key] = [row[key]["cpu_util_avg_percent"]]
                throttles[key] = [row[key]["cpu_throttle"]]

    return utils, throttles


def get_current_configs(filepath):
    #experiment_no = 1
    #path = base_path + str(profile) + "_" + str(experiment_no)
    txt_file = glob.glob(filepath + '/*.txt')
    configs = {}
    container_ids = {}
    js_file = open(txt_file[0])
    data = json.load(js_file)
    for row in data:
        for key in row:
            configs[key] = row[key]['cpu_core'] * row[key]['replica']
            container_ids[key] = row[key]["settings"]
    return configs, container_ids

