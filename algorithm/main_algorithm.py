import json
import time
import datetime
from algorithm.db_utils import HistoryDB
# from algorithm_data_hr import CONTAINER_LIST, CONTAINER_UTIL_LISTS, CONTAINER_UTIL_LIMITS, CONTAINER_THROTTLE_LIMITS, \
#     NUMBER_OF_CONTAINERS, DEFAULT_CONFIGS
from algorithm_data_ss import CONTAINER_LIST, CONTAINER_UTIL_LISTS, CONTAINER_UTIL_LIMITS, CONTAINER_THROTTLE_LIMITS, \
    NUMBER_OF_CONTAINERS, DEFAULT_CONFIGS
from system_metrics.metric_collector import collect_prometheus_data
from system_metrics.collector_backend import get_response_latency, get_request_per_seconds
from system_metrics.metrics_processing import process_prometheus_data, process_configurations
from algorithm_utils import get_workload_range, choose_containers, update_configurations, apply_configurations
from dynamic_thresholds import get_stopping_threshold


def apply_configuration_by_workload(SLO, workload_range_id):
    previous_configuration = history.get_last_configuration(SLO, workload_range_id)
    if previous_configuration:
        print("Got configurations.json from DB")
        if previous_configuration['next_configs']:
            apply_configurations(previous_configuration['next_configs'])
        else:
            print("There are no next configuration from DB")
            higher_cost_config = history.get_configuration_with_higher_cost(SLO, workload_range_id,
                                                                            previous_configuration['cost'])
            if higher_cost_config:
                apply_configurations(higher_cost_config['current_configs'])
            else:
                apply_configurations(DEFAULT_CONFIGS)
    else:
        apply_configurations(DEFAULT_CONFIGS)


def get_prometheus_data():
    # collect system metrics for all containers
    raw_metrics = collect_prometheus_data(CONTAINER_LIST, duration=evaluation_period)

    # process these metrics
    system_metrics = process_prometheus_data(raw_metrics, percentile=0.99)

    # gather system configuration and metadata such as node, id, settings
    system_configs, system_metadata = process_configurations(raw_metrics)

    # add current utilization to the utilization list
    for x in system_metrics:
        CONTAINER_UTIL_LISTS[x].append(system_metrics[x]['cpu_utilization'])

    # cost is represented as total CPU
    config_cost = sum(system_configs.values())

    return system_metrics, system_configs, system_metadata, config_cost


def algorithm_loop(profile, last_inserted_id):
    while profile < 40:

        # get current rps, end-to-end response time, and workload range
        rps = get_request_per_seconds('frontend', duration=evaluation_period)

        if float(rps) < 400:
            print("waiting for real workloads")
            time.sleep(5)
            #profile += 1
            break
            # continue
        # latency = get_response_latency('frontend', duration=120, percentile=0.99)

        range_id, workload_range = get_workload_range(rps)

        # update the latency of the last configuration
        # if last_inserted_id >= 0:
        #     history.update_latency_of_last_config(last_inserted_id, latency)

        # apply previous update configuration
        apply_configuration_by_workload(SLO, range_id)

        current_settings = {"experiment_id": profile, "metrics": "",
                            "response": "", "time": datetime.datetime.now(), "rps": rps,
                            "delta_response": -1, "slo": SLO, "range_id": range_id, "rps_range": workload_range,
                            "cost": "", "delta_si": -1, "n_s": -1, "threshold": -1,
                            "current_configs": "", "next_configs": "",
                            "container_stats": "None", "early_slo_violation": 1,
                            "detection_time": ""}

        # EARLY DETECTION
        duration = time.time()
        early_detection_window = 10
        slo_violation = False
        short_evaluation_period = 10
        responses_list = []
        while time.time() <= duration + evaluation_period and not slo_violation:
            time.sleep(short_evaluation_period)

            latency = get_response_latency(container_name='frontend', duration=early_detection_window, percentile=0.99)
            if latency:
                responses_list.append(latency)
            else:
                responses_list.append(0)
            print("The current latency (ms) and early detection window(s): ", latency, early_detection_window)

            if latency and float(latency) > SLO + 5:

                system_metrics, system_configs, system_metadata, config_cost = get_prometheus_data()

                # making a dictionary for all parameters and settings
                current_settings["metrics"] = system_metrics
                current_settings["response"] = float(latency)
                current_settings["cost"] = config_cost
                current_settings["current_configs"] = system_configs
                current_settings["early_slo_violation"] = 1
                current_settings["detection_time"] = early_detection_window
                current_settings["responses"] = responses_list

                # inserting data into dictionary
                history.insert_into_table(current_settings)
                profile += 1
                slo_violation = True

            early_detection_window += short_evaluation_period

            # time.sleep(30)
        if slo_violation:
            continue

        rps = float(get_request_per_seconds('frontend', duration=evaluation_period))
        latency = float(get_response_latency('frontend', duration=evaluation_period, percentile=0.99))
        responses_list.append(str(latency))
        print("The RPS and Latency: ", rps, latency)

        system_metrics, system_configs, system_metadata, config_cost = get_prometheus_data()

        # making a dictionary for all parameters and settings
        current_settings["metrics"] = system_metrics
        current_settings["response"] = float(latency)
        current_settings["cost"] = config_cost
        current_settings["current_configs"] = system_configs
        current_settings["early_slo_violation"] = 0
        current_settings["detection_time"] = evaluation_period
        current_settings["rps"] = rps
        current_settings["next_configs"] = system_configs
        current_settings["responses"] = responses_list

        # get Q value which will be used to calculate SLO threshold
        # if the Q value is negative, conduct enough experiments to apply ML
        q_value = get_stopping_threshold(SLO, range_id, workload_range, history, lower_bound)
        print("Q value is ", q_value)
        if q_value == -1:
            profile += 1
            print(current_settings)
            last_inserted_id = history.insert_into_table(current_settings)
            print("No changes in configs. Conducting same experiments...")
            print("######################")
            # apply_configurations(DEFAULT_CONFIGS, system_metadata)
            # time.sleep(60)
            continue
        # iteration += 1
        # if iteration == 10:
        #     break
        # calculate threshold based on Q value and workload range
        threshold = (((lower_bound * SLO - q_value) / (workload_range["max"] - workload_range["min"])) * (
                rps - workload_range["min"])) + q_value

        print("Threshold for RPS: %d is %d" % (rps, threshold))

        # figure out how far the latency is from threshold, 0 if latency exceeded threshold (violating SLO?)
        delta_response = max(0, threshold - latency)
        current_settings["delta_response"] = delta_response
        current_settings["threshold"] = threshold

        # latency is violating threshold (not SLO violation all the time)

        if latency < threshold:
            # update each container's utilization limit with current utilizations
            for container in system_metrics.keys():  # update limit of containers.
                # max_value = max(system_metrics[container]['cpu_utilization'])
                if system_metrics[container]['cpu_utilization'] > CONTAINER_UTIL_LIMITS[container]:
                    CONTAINER_UTIL_LIMITS[container] = system_metrics[container]['cpu_utilization']

            # update threshold of each container with current value
            for x in system_metrics.keys():  # update throttle of containers
                if system_metrics[x]['throttles'] >= CONTAINER_THROTTLE_LIMITS[x]:
                    CONTAINER_THROTTLE_LIMITS[x] = system_metrics[x]['throttles']

            # calculate N_S for candidate container numbers
            # select_container_numbers = int((number_of_containers / alpha) * (delta_response / SLO))
            select_container_numbers = int((NUMBER_OF_CONTAINERS / alpha) * (delta_response / threshold))

            # check if # candidate containers (n_s) greater than total container,
            if select_container_numbers > NUMBER_OF_CONTAINERS:
                select_container_numbers = NUMBER_OF_CONTAINERS

            # now choose candidate containers based on n_s, systems metrics (utils, throttles) and current configs
            candidate_containers = choose_containers(select_container_numbers, system_metrics, system_configs)

            # random_explore = 1 - ((number_of_containers - select_container_numbers) / number_of_containers)
            # random_explore = 0.2
            # random_explore = delta_response / (alpha * SLO* (profile-10))

            # get new configurations.json based on candidate containers and settings such as alpha,beta, threshold and random
            # exploration
            new_configs, delta_si = update_configurations(candidate_containers, system_configs, alpha, beta, threshold,
                                                          delta_response, random_exploration=0)

            current_settings["next_configs"] = new_configs
            current_settings["delta_si"] = delta_si
            current_settings["n_s"] = select_container_numbers
            current_settings['cost'] = sum(system_configs.values())
            print("N_s: ", current_settings["n_s"], "Threshold: ", current_settings["threshold"])
            print("New configs: ", current_settings["next_configs"])

        else:
            """
            select previous configuration that didn't violate SLO
            """
            print("Response time exceeded threshold. Will go back to history")
            current_settings["next_configs"] = ""

        history.insert_into_table(current_settings)
        # early detection of SLO
        # current_time = time.time()
        # while time.time() < current_time + 120:
        #     rps, latency = get_rps_and_latency('frontend', duration=30, percentile=0.99)
        #     if latency < SLO:
        #         time.sleep(10)
        #     else:
        #         break

        profile += 1
        if latency < 10:
            break
        # evaluation period
        # time.sleep(evaluation_period)
        # current_settings['response'] = latency
        # last_inserted_id = history.insert_into_table(current_settings)


if __name__ == '__main__':
    SLO = 50
    alpha = 0.6
    beta = 0.3
    history = HistoryDB()
    HISTORY_WEIGHT = 1
    lower_bound = 1
    profile = 1
    last_db_entry = -1
    evaluation_period = 120  # in seconds (2 mins)

    # total 9.1
    temp1 = {'hotel-reserv-frontend': 1.4, 'hotel-reserv-geo': 0.7, 'hotel-reserv-geo-mongo': 0.3, 'hotel-reserv-profile': 1.5, 'hotel-reserv-profile-mmc': 0.3, 'hotel-reserv-profile-mongo': 0.3, 'hotel-reserv-rate': 0.3, 'hotel-reserv-rate-mmc': 0.3, 'hotel-reserv-rate-mongo': 0.3, 'hotel-reserv-recommendation': 0.3, 'hotel-reserv-recommendation-mongo': 0.3, 'hotel-reserv-reservation': 1.0, 'hotel-reserv-reservation-mmc': 0.3, 'hotel-reserv-reservation-mongo': 0.3, 'hotel-reserv-search': 0.7, 'hotel-reserv-user': 0.5, 'hotel-reserv-user-mongo': 0.3}

    # total 30.4
    temp2 = {'hotel-reserv-frontend': 2.8, 'hotel-reserv-geo': 2.0, 'hotel-reserv-geo-mongo': 1.5, 'hotel-reserv-profile': 3.0, 'hotel-reserv-profile-mmc': 1.5, 'hotel-reserv-profile-mongo': 1.5, 'hotel-reserv-rate': 1.5, 'hotel-reserv-rate-mmc': 1.5, 'hotel-reserv-rate-mongo': 1.5, 'hotel-reserv-recommendation': 1.5, 'hotel-reserv-recommendation-mongo': 1.5, 'hotel-reserv-reservation': 2.1, 'hotel-reserv-reservation-mmc': 2.1, 'hotel-reserv-reservation-mongo': 1.5, 'hotel-reserv-search': 2.8, 'hotel-reserv-user': 1.0, 'hotel-reserv-user-mongo': 1.5}

    # total 12.4
    temp3 = {'hotel-reserv-frontend': 2.0, 'hotel-reserv-geo': 1.0, 'hotel-reserv-geo-mongo': 0.3, 'hotel-reserv-profile': 2.1, 'hotel-reserv-profile-mmc': 0.5, 'hotel-reserv-profile-mongo': 0.3, 'hotel-reserv-rate': 0.5, 'hotel-reserv-rate-mmc': 0.3, 'hotel-reserv-rate-mongo': 0.3, 'hotel-reserv-recommendation': 0.5, 'hotel-reserv-recommendation-mongo': 0.3, 'hotel-reserv-reservation': 1.5, 'hotel-reserv-reservation-mmc': 0.5, 'hotel-reserv-reservation-mongo': 0.3, 'hotel-reserv-search': 1.0, 'hotel-reserv-user': 0.7, 'hotel-reserv-user-mongo': 0.3}

    apply_configurations(temp3)
    # algorithm_loop(profile, last_db_entry)
    # total = 0
    # for k,v in temp2.items():
    #     total += v
    # print(total)
