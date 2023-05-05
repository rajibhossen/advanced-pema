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

base_path = '/home/ridl/rajibs_work/advanced_pema/workload_module/sock_shop/log_data/early_detection/config_2/'
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


# def cumulative_latency():
#     base_path = '/home/ridl/rajibs_work/advanced_pema/workload_module/log_data/hr_data/datasets_3_cpu_12.4/'
#     requests_per_seconds = [200, 250, 300, 350, 400, 450, 500, 550, 600]
#     # final_df = {'RPS':[], 'Total Latency': [], 'Time Window': [], 'Lateny': []}
#     # final_df = pd.DataFrame({'RPS':[], 'Total Latency': [], 'Time Window': [], 'Lateny': []})
#     final_data = []
#     percentile = 0.95
#     window = 10
#     for rps in requests_per_seconds:
#         for profile in range(3):
#             file_name = 'rps_' + str(rps) + '_iteration_' + str(profile)
#             data_path = base_path + file_name + '/'
#             dataset = pd.read_csv(data_path + file_name + '.csv', index_col='arrival_time', parse_dates=True)
#
#             total_latency = dataset.latency.quantile(percentile) * 1000
#             # actual_rps = len(dataset.index) / 120.0
#
#             # print(dataset.head())
#             detection_window = {}
#             actual_rps = {}
#             start = window
#             responses = []
#             start_time = dataset.index[0]
#
#             for index, row in dataset.iterrows():
#                 end_time = start_time + datetime.timedelta(0, start)
#                 responses.append(row['latency'])
#                 if index > end_time:
#                     detection_window[start] = np.percentile(responses, percentile * 100) * 1000
#                     actual_rps[start] = len(responses) / start
#                     start += window
#             for k, v in detection_window.items():
#                 # temp = pd.DataFrame({'RPS': actual_rps, 'Total Latency': total_latency, 'Time Window': k, 'Lateny': v})
#
#                 temp = [rps, actual_rps[k], total_latency, k, v]
#                 final_data.append(temp)
#                 # final_df = pd.concat([final_df, temp], ignore_index=True)
#                 # print(final_df)
#     with open(base_path + "combined_datasets_with_cumulative_methods_p" + str(percentile) + "_" + str(
#             window) + "_seconds_apart_config_2.csv", 'w', newline='') as f:
#         writer = csv.writer(f)
#         # writer.writerow('')
#         writer.writerows(final_data)
#     # print(final_data)


def detect_slo_by_total_counting():
    base_path = '/home/ridl/rajibs_work/advanced_pema/workload_module/sock_shop/log_data/early_detection/config_2/'
    requests_per_seconds = [100, 200, 300, 400, 500, 600, 700, 800]
    # requests_per_seconds = {200: 225, 250: 275, 300: 350, 350: 400, 400: 450, 450: 500, 500: 550}
    final_data = []
    slo_variations = [60, 70, 80, 90, 100]
    percentile = 0.99
    for set_slo in slo_variations:
        for expected_rps in requests_per_seconds:
            for profile in range(4):
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

    with open(base_path + "combined_datasets_with_total_counter_methods_p" + str(percentile) + "_configs_2.csv", 'w',
              newline='') as f:
        writer = csv.writer(f)
        writer.writerows(final_data)
    # print(final_data)


def get_slo_difference_and_time_taken_for_total_counting():
    x_values = []
    y_values = []
    final_list = []
    # Open file
    for i in range(2, 3):
        filename = base_path + 'ss_combined_datasets_with_total_counter_methods_p0.99_configs_' + str(i) + '.csv'
        with open(filename) as file_obj:
            # Create reader object by passing the file

            next(file_obj)

            # object to reader method
            reader_obj = csv.reader(file_obj)

            # Iterate over each row in the csv
            # file using reader object
            for row in reader_obj:
                total_latency = float(row[2])
                slo = float(row[3])
                time_to_detect = float(row[4])
                if time_to_detect == 0:
                    time_to_detect = 120
                latency_difference = total_latency - slo
                if latency_difference > 0:
                    x_values.append(total_latency - slo)
                    y_values.append(time_to_detect)

    for x in range(len(x_values)):
        final_list.append([x_values[x], y_values[x]])

    with open(base_path + 'ss_slo_difference_and_time_taken_for_total_counting_config_2.csv', 'w') as myfile:
        wr = csv.writer(myfile)
        wr.writerows(final_list)


def detect_slo_by_cumulative_counting():
    base_path = '/home/ridl/rajibs_work/advanced_pema/workload_module/sock_shop/log_data/early_detection/config_2/'
    requests_per_seconds = [100, 200, 300, 400, 500, 600, 700, 800]
    # requests_per_seconds = {200: 225, 250: 275, 300: 350, 350: 400, 400: 450, 450: 500, 500: 550}
    slo_variations = [60, 70, 80, 90, 100]
    percentile = 0.99
    windows = [10, 20, 30, 40, 50, 60]
    # window = 20
    for window in windows:
        final_data = []
        # set_slo = 30
        for set_slo in slo_variations:
            for expected_rps in requests_per_seconds:
                for profile in range(4):
                    file_name = 'rps_' + str(expected_rps) + '_iteration_' + str(profile)
                    data_path = base_path + file_name + '/'
                    dataset = pd.read_csv(data_path + file_name + '.csv', index_col='arrival_time', parse_dates=True)

                    total_latency = dataset.latency.quantile(percentile) * 1000
                    actual_rps = len(dataset.index) / 120.0
                    start_time = dataset.index[0]
                    end_time = None
                    time_taken_to_slo_violation = 120

                    total_violation_tolerated = expected_rps * window * (1 - percentile)
                    print("Total SLO Violation Tolerable Limit: %s for RPS: %s and time: %s " % (
                    total_violation_tolerated, expected_rps, window))
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
                            print("SLO Violation Tolerable Limit: %s for RPS: %s and time: %s " % (
                            total_violation_tolerated, expected_rps, window))

                    if end_time:
                        time_taken_to_slo_violation = (end_time - start_time).total_seconds()

                    # projected rps, actual rps, actual latency, time_taken
                    temp = [expected_rps, actual_rps, total_latency, set_slo, time_taken_to_slo_violation]
                    final_data.append(temp)
            # print("Total SLO Violation: ", counter)
            # print("Time Taken to slo violation: ", time_taken_to_slo_violation)

        with open(base_path + "combined_datasets_with_cumulative_counting_p" + str(percentile) + "_window_" + str(
                window) + "_configs_1.csv", 'w',
                  newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['expected_rps', 'actual_rps', 'total_latency', 'slo', 'time_taken_to_detect'])
            writer.writerows(final_data)


def accuracy_determination_for_cumulative_window():
    # Open file
    false_detection = 0
    true_detection = 0
    detection_time_distribution = {'10': 0, '20': 0, '30': 0, '40': 0, '50': 0, '60': 0, '70': 0, '80': 0, '90': 0,
                                   '100': 0, '110': 0,
                                   '120': 0}
    total_slo_violation = 0
    total_points = 0
    windows = [10, 20, 30, 40, 50, 60]
    for window in windows:
        with open(base_path + 'combined_datasets_with_cumulative_counting_p0.99_window_'+str(window)+'_configs_2.csv') as file_obj:
            # Create reader object by passing the file
            # heading = next(file_obj)

            # object to reader method
            reader_obj = csv.reader(file_obj)
            header = next(reader_obj)
            # Iterate over each row in the csv
            # file using reader object
            for row in reader_obj:

                expected_rps = float(row[0])
                actual_rps = float(row[1])
                # if expected_rps == 500:
                total_latency = float(row[2])
                slo = float(row[3])
                detection_time = float(row[4])

                total_points += 1

                if total_latency > slo:
                    total_slo_violation += 1

                if detection_time < 10:
                    detection_time_distribution['10'] += 1
                elif detection_time < 20:
                    detection_time_distribution['20'] += 1
                elif detection_time < 30:
                    detection_time_distribution['30'] += 1
                elif detection_time < 40:
                    detection_time_distribution['40'] += 1
                elif detection_time < 50:
                    detection_time_distribution['50'] += 1

                if total_latency < slo and detection_time < 120:
                    false_detection += 1
                elif total_latency < slo and detection_time == 120:
                    true_detection += 1

        accuracy = 100 - (false_detection / total_points)*100
        print(window, accuracy)
    # print(false_detection, true_detection, total_points)
    # print(detection_time_distribution)
    # print(total_slo_violation)


def cumulative_window_vs_average_time_taken():
    windows = [10, 20, 30, 40, 50, 60]
    time_taken = []
    for window in windows:
        filename = base_path + '/combined_datasets_with_cumulative_counting_p0.99_window_' + str(window) + '_configs_2.csv'

        # Open file
        detection_time_list = []
        with open(filename) as file_obj:
            # Create reader object by passing the file
            # heading = next(file_obj)

            # object to reader method
            reader_obj = csv.reader(file_obj)
            header = next(reader_obj)
            # Iterate over each row in the csv
            # file using reader object
            for row in reader_obj:

                expected_rps = float(row[0])
                actual_rps = float(row[1])
                # if expected_rps == 500:
                total_latency = float(row[2])
                slo = float(row[3])
                detection_time = float(row[4])
                if detection_time < 120:
                    detection_time_list.append(detection_time)

        time_taken.append(sum(detection_time_list) / len(detection_time_list))
    print(time_taken)


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


def get_end_to_end_latency():
    base_path = '/home/ridl/rajibs_work/advanced_pema/workload_module/sock_shop/log_data/vertical_and_horizontal/carts_x3_c0.6/'
    requests_per_seconds = [400]
    # requests_per_seconds = {200: 225, 250: 275, 300: 350, 350: 400, 400: 450, 450: 500, 500: 550}
    final_data = []
    # slo_variations = [60, 70, 80, 90, 100]
    responses = []
    percentile = 0.99
    for expected_rps in requests_per_seconds:
        for profile in range(4):
            file_name = 'rps_' + str(expected_rps) + '_iteration_' + str(profile)
            data_path = base_path + file_name + '/'
            dataset = pd.read_csv(data_path + file_name + '.csv', index_col='arrival_time', parse_dates=True)

            total_latency = dataset.latency.quantile(percentile) * 1000
            actual_rps = len(dataset.index) / 120.0
            responses.append(total_latency)
            # print(total_latency)
    print(sum(responses)/len(responses))


if __name__ == '__main__':
    get_end_to_end_latency()
    # first merge requests from all logs into one file
    #merge_requests

    # determine if slo violated by total counting
    # detect_slo_by_total_counting()

    # calculate slo differences and total time took to detect slo violations
    #get_slo_difference_and_time_taken_for_total_counting()

    # determine if slo violated by various window size
    # detect_slo_by_cumulative_counting()

    # determine accuracy for detecting slo for each window
    # accuracy_determination_for_cumulative_window()

    # calculate slo detection time taken for each windows
    # cumulative_window_vs_average_time_taken()

