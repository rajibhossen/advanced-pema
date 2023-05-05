import json
import os
import random
import subprocess as sp
import sys
import time
import numpy as np
from scipy.interpolate import interp1d
from metrics_collection.prometheus_data import get_resource_utilization


def run_program(rate, experiment_time, experiment_no, threads):
    procs = []
    # two process, 1,2
    # params - script name, rate, runtime (s), log file name
    # print(threads)
    for i in range(1, threads):
        p = sp.Popen(
            [sys.executable, "load_test.py", rate, experiment_time,
             experiment_no + "/data_p" + rate + "_t" + str(threads) + "_" + str(i)])
        procs.append(p)

    for p in procs:
        p.wait()


def collect_metrics():
    container_data = []
    for container in container_list:
        container_data.append(get_resource_utilization(container, int(EXPERIMENT_TIME / 60)))
        # print(get_resource_utilization(container))
    return container_data

def avoid_cold_start():
    path = "load_data/algorithm_navigation/temps"

    if not os.path.exists(path):
        os.makedirs(path)

    run_program(str(45), str(60), "temps", 3)
    # sp.call(['sh', './flush_db.sh'])


def get_poisson_rate(requests):
    # poisson = 32684 * requests**(-1*1.049)
    rps = [840.5083333, 708.1833333, 613.3666667, 544.9333333, 483.4333333, 432.8, 393.3, 364.0583333, 339.7416667,
           315.3416667, 295]
    poisson = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75]
    #
    x = np.array(rps)
    y = np.array(poisson)
    f = interp1d(x, y)
    poisson = f(np.array(requests))
    return int(poisson)


if __name__ == '__main__':
    SLO = 50

    # ranges = {
    #     1: {"min": 100, "max": 300},
    #     2: {"min": 301, "max": 500},
    #     3: {"min": 501, "max": 700}
    # }

    # ranges = {
    #     1: {"min": 100, "max": 150},
    #     2: {"min": 151, "max": 200},
    #     3: {"min": 201, "max": 250},
    #     4: {"min": 251, "max": 300},
    #     5: {"min": 301, "max": 350},
    #     6: {"min": 351, "max": 400},
    #     7: {"min": 401, "max": 450},
    #     8: {"min": 451, "max": 500},
    #     9: {"min": 501, "max": 550},
    #     10: {"min": 551, "max": 600},
    #     11: {"min": 601, "max": 650},
    #     12: {"min": 651, "max": 700},
    #     13: {"min": 701, "max": 750},
    #     14: {"min": 751, "max": 800}
    # }


    profile = 1
    experiment_no = 1
    number_of_containers = len(container_list)
    number_of_process = 10


    avoid_cold_start()
    # avoid_cold_start()
    # avoid_cold_start()

    data_size = 30
    rps_array = [305, 315, 325, 335, 345, 355, 365, 375, 385, 395]
    while data_size:
        data_size -= 1
        print("BEGIN EXPERIMENT: ", profile)

        range_id = 2
        # RPS = 100
        # RPS = request_per_seconds.pop(0)
        # if rps_array:
        #     RPS = rps_array.pop(random.randrange(len(rps_array)))
        # else:
        #     RPS = random.randint(575, 595)

        RPS = random.randint(375, 395)
        # RPS = request_per_seconds.pop(0)

        # RPS = 650
        # if profile > 10:
        #     beta = 0.2
        # if profile > 20:
        #     beta = 0.1
        # if profile > 40:
        #     beta = 0.05



        rate = get_poisson_rate(RPS)

        print("Predicted RPS is: ", RPS)
        # print(previous_data)

        current_settings = {"config_id": profile}
        config_name = str(profile) + "_"
        path = "algorithm_data/" + config_name + str(experiment_no)

        if not os.path.exists(path):
            os.makedirs(path)

        # main experiments
        print("Starting the main experiments for 2 minutes with poisson: ", rate)
        run_program(str(rate), str(EXPERIMENT_TIME), config_name + str(experiment_no), number_of_process + 1)

        print("Collecting metrics....")
        metrics = collect_metrics()
        with open(path + "/p" + str(rate) + ".txt", 'w') as filehandle:
            json.dump(metrics, filehandle)

        # flashing databases
        # sp.call(['sh', './flush_db.sh'])



            # CODE for dynamic range

            # if select_container_numbers < 3 and select_container_numbers != -1:
            #     if range_id in ns_changed_total:
            #         ns_changed_total[range_id] += 1
            #     else:
            #         ns_changed_total[range_id] = 0
            #
            # if range_id in ns_changed_total and ns_changed_total[range_id] == 5:
            #     ns_changed_total[range_id] = 0
            #     available_range_id = 0
            #     for x in ranges:
            #         if available_range_id <= x:
            #             available_range_id = x
            #     available_range_id += 1
            #
            #     range_min = ranges[range_id]["min"]
            #     range_max = ranges[range_id]["max"]
            #
            #     if range_max - range_min < 10:
            #         continue
            #
            #     ranges[range_id]["min"] = range_min
            #     ranges[range_id]["max"] = range_min + int((range_max - range_min) / 2)
            #
            #     ranges[available_range_id] = {}
            #     ranges[available_range_id]["min"] = range_min + int((range_max - range_min) / 2) + 1
            #     ranges[available_range_id]["max"] = range_max
            #
            #     ns_changed_total[available_range_id] = 0
            #
            #     save_q_value(SLO, available_range_id, q_value, QValueDB())
            #     current_settings["range_id"] = available_range_id
            #     current_settings["rps_range"] = ranges[available_range_id]
            #     history.insert_into_table(current_settings)

        end = time.time()
        duration = end - start
        print("Time to apply changes: ", duration)
        print("####################")
        profile += 1
        # time.sleep(30)
