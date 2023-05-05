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

base_path = '/home/ridl/rajibs_work/advanced_pema/workload_module/log_data/hr_data/'
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
    # rps_list = ['120']
    profiles = [str(x) for x in range(3)]
    slot_id = 63
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
            print("Latency is: ", final_df.latency.quantile(0.99))
            print("Done for ", experiment_name)
            slot_id += 1
    # print(final_df.head())


def cumulative_latency():
    base_path = '/home/ridl/rajibs_work/advanced_pema/workload_module/log_data/hr_data/datasets_3_cpu_12.4/'
    requests_per_seconds = [200, 250, 300, 350, 400, 450, 500, 550, 600]
    # final_df = {'RPS':[], 'Total Latency': [], 'Time Window': [], 'Lateny': []}
    # final_df = pd.DataFrame({'RPS':[], 'Total Latency': [], 'Time Window': [], 'Lateny': []})
    final_data = []
    percentile = 0.95
    window = 10
    for rps in requests_per_seconds:
        for profile in range(3):
            file_name = 'rps_' + str(rps) + '_iteration_' + str(profile)
            data_path = base_path + file_name + '/'
            dataset = pd.read_csv(data_path + file_name + '.csv', index_col='arrival_time', parse_dates=True)

            total_latency = dataset.latency.quantile(percentile) * 1000
            # actual_rps = len(dataset.index) / 120.0

            # print(dataset.head())
            detection_window = {}
            actual_rps = {}
            start = window
            responses = []
            start_time = dataset.index[0]

            for index, row in dataset.iterrows():
                end_time = start_time + datetime.timedelta(0, start)
                responses.append(row['latency'])
                if index > end_time:
                    detection_window[start] = np.percentile(responses, percentile*100) * 1000
                    actual_rps[start] = len(responses) / start
                    start += window
            for k, v in detection_window.items():
                # temp = pd.DataFrame({'RPS': actual_rps, 'Total Latency': total_latency, 'Time Window': k, 'Lateny': v})

                temp = [rps, actual_rps[k], total_latency, k, v]
                final_data.append(temp)
                # final_df = pd.concat([final_df, temp], ignore_index=True)
                # print(final_df)
    with open(base_path + "combined_datasets_with_cumulative_methods_p"+str(percentile)+"_"+str(window)+"_seconds_apart_config_2.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        # writer.writerow('')
        writer.writerows(final_data)
    # print(final_data)


def detect_slo_by_counting():
    base_path = '/home/ridl/rajibs_work/advanced_pema/workload_module/log_data/hr_data/'
    requests_per_seconds = [200, 250, 300, 350, 400, 450, 500, 550, 600]
    #requests_per_seconds = {200: 225, 250: 275, 300: 350, 350: 400, 400: 450, 450: 500, 500: 550}
    final_data = []
    slo_variations = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    percentile = 0.95
    for set_slo in slo_variations:
        for expected_rps in requests_per_seconds:
            for profile in range(3):
                file_name = 'rps_' + str(expected_rps) + '_iteration_' + str(profile)
                data_path = base_path + file_name + '/'
                dataset = pd.read_csv(data_path + file_name + '.csv', index_col='arrival_time', parse_dates=True)

                total_latency = dataset.latency.quantile(percentile) * 1000
                actual_rps = len(dataset.index) / 120.0
                start_time = dataset.index[0]
                end_time = None
                time_taken_to_slo_violation = 120
                total_violation_tolerated = expected_rps * 120 * (1 - percentile)
                print("Total SLO Violation Tolerable Limit for RPS: ", total_violation_tolerated, expected_rps)
                counter = 0

                for index, row in dataset.iterrows():
                    if row['latency'] * 1000 > set_slo:
                        counter += 1

                    if counter > total_violation_tolerated:
                        end_time = index
                        break
                if end_time:
                    time_taken_to_slo_violation = (end_time - start_time).total_seconds()

                # projected rps, actual rps, actual latency, time_taken
                temp = [expected_rps, actual_rps, total_latency, set_slo, time_taken_to_slo_violation]
                final_data.append(temp)
            # print("Total SLO Violation: ", counter)
            # print("Time Taken to slo violation: ", time_taken_to_slo_violation)

    with open(base_path + "combined_datasets_with_counter_methods_p" + str(percentile) + "_configs_3.csv", 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(final_data)
    # print(final_data)


def detect_slo_by_cumulative_counting():
    base_path = '/home/ridl/rajibs_work/advanced_pema/workload_module/log_data/hr_data/datasets_1_cpu_9.1/'
    requests_per_seconds = [200, 250, 300, 350, 400, 450, 500]
    # requests_per_seconds = {200: 225, 250: 275, 300: 350, 350: 400, 400: 450, 450: 500, 500: 550}
    final_data = []
    slo_variations = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    percentile = 0.99
    windows = [10, 20, 30, 40, 50, 60]
    # window = 20
    for window in windows:
        # set_slo = 30
        for set_slo in slo_variations:
            for expected_rps in requests_per_seconds:
                for profile in range(5):
                    file_name = 'rps_' + str(expected_rps) + '_iteration_' + str(profile)
                    data_path = base_path + file_name + '/'
                    dataset = pd.read_csv(data_path + file_name + '.csv', index_col='arrival_time', parse_dates=True)

                    total_latency = dataset.latency.quantile(percentile) * 1000
                    actual_rps = len(dataset.index) / 120.0
                    start_time = dataset.index[0]
                    end_time = None
                    time_taken_to_slo_violation = 120

                    total_violation_tolerated = expected_rps * window * (1 - percentile)
                    print("Total SLO Violation Tolerable Limit: %s for RPS: %s and time: %s "%(total_violation_tolerated, expected_rps, window))
                    counter = 0

                    for index, row in dataset.iterrows():
                        if row['latency'] * 1000 > set_slo:
                            counter += 1

                        if counter > total_violation_tolerated:
                            end_time = index
                            break

                        # track for 10 seconds, if exceed 10 seconds mark, increase by another 10 seconds
                        if index > start_time + datetime.timedelta(0, window):
                            # window += 10
                            total_violation_tolerated += expected_rps * window * (1 - percentile)
                            start_time = index
                            print("SLO Violation Tolerable Limit: %s for RPS: %s and time: %s "%(total_violation_tolerated, expected_rps, window))

                    if end_time:
                        time_taken_to_slo_violation = (end_time - start_time).total_seconds()

                    # projected rps, actual rps, actual latency, time_taken
                    temp = [expected_rps, actual_rps, total_latency, set_slo, time_taken_to_slo_violation]
                    final_data.append(temp)
            # print("Total SLO Violation: ", counter)
            # print("Time Taken to slo violation: ", time_taken_to_slo_violation)

        with open(base_path + "combined_datasets_with_cumulative_counting_p" + str(percentile) + "_window_"+str(window)+"_configs_1.csv", 'w',
                  newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['expected_rps', 'actual_rps', 'total_latency', 'slo', 'time_taken_to_detect'])
            writer.writerows(final_data)


def different_end_to_end():
    rpss = []
    avgs = []
    percentiles = []

    # p = str(profile) + "/" + str(experiment_no)
    x = []
    responses = []

    data_files = load_data_files()
    for temp in data_files:
        df = temp
        df1 = df.groupby("user")["response_time"].agg(["count", "sum"])
        print(df1)
        for a in df1["sum"].values:
            responses.append(a)

        x.append(df1["count"].sum())

    # print(responses)
    rpss.append(sum(x) / 120)
    # avgs.append((sum(responses) / len(responses)) * 1000)
    percentile_response = np.percentile(np.array(responses), 99)
    percentiles.append(percentile_response * 1000)
    print(rpss, percentiles)


def latency_from_list():
    file = open('responses_list_20mins.txt', 'r')
    responses_list = file.readlines()
    responses_list = [eval(i) for i in responses_list]
    per_set_sec = []
    for i in range(0, len(responses_list), 12):
        # aggregated = responses_list[i] + responses_list[i+1] + responses_list[i+2] + responses_list[i+3]

        aggregated_list = []
        for j in range(i + 12):
            aggregated_list.extend(responses_list[i])

        per_set_sec.append(np.quantile(aggregated_list, 0.99) * 1000)
    # print(np.quantile(per_set_sec, 0.99)*1000)
    print(per_set_sec)
    print(len(per_set_sec))


def redis_end_to_end():
    redis_client = redis.Redis(host='192.168.2.62', port=6379, db=0)
    total_responses_list = []
    total_rps_list = []
    time_passed = 0
    while time_passed <= 1200:
        rps = redis_client.get("RPS")
        responses_list = redis_client.get("responses")
        # if rps and responses_list:
        if not rps and not responses_list:
            print("waiting")
            time.sleep(1)
            continue
        rps = float(rps)
        total_rps_list.append(rps)

        responses_list = eval(responses_list)
        total_responses_list.append(responses_list)
        time_passed += 10
        percentile_99 = np.quantile(responses_list, 0.99) * 1000
        print("response time at 10 s is :%s " % (percentile_99))
        print("RPS at %s s is: %s" % (time_passed, sum(total_rps_list) / time_passed))

        time.sleep(10)
    # print(total_responses_list)
    file = open('responses_list_20mins.txt', 'w')
    for item in total_responses_list:
        file.write(str(item) + "\n")
    file.close()
    print(time_passed)


# different_end_to_end()
# data = get_end_to_end()
# redis_end_to_end()
# latency_from_list()

# merge_requests()
# cumulative_latency()
detect_slo_by_cumulative_counting()
# detect_slo_by_counting()
