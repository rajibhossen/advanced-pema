import random
import threading
from algorithm_data_hr import DEFAULT_CONFIGS, CONTAINER_UTIL_LIMITS
from action_executor import agent
import numpy as np
from system_metrics.collector_backend import retreive_container_metadata

def calculate_delta_si(beta, delta_response, alpha, threshold):
    value = (beta / alpha) * min((delta_response / threshold), alpha)
    return value


def update_configurations(candidate_configs, current_configs, alpha, beta, threshold, delta_response,
                          random_exploration=0.0):
    """
    Update the system configurations.json based on the given parameters.

    :param candidate_configs: A dictionary containing the candidate configurations.json
    :param current_configs: A dictionary containing the current configurations.json
    :param alpha: A float that represents the weight for the configuration metric
    :param beta: A float that represents the weight for the performance metric
    :param threshold: A float that represents the threshold for the delta_si calculation
    :param delta_response: A float that represents the change in the response time
    :param random_exploration: A float that represents the probability of choosing a random configuration
    :return: A tuple that contains a dictionary of the new configurations.json and a float delta_si
    """
    new_configs = {}
    delta_si = calculate_delta_si(beta, delta_response, alpha, threshold)
    if random.uniform(0, 1) < random_exploration:
        for x in candidate_configs:
            new_configs[x] = max(DEFAULT_CONFIGS[x], round((current_configs[x] * (1 + delta_si)), 1))

        for x in current_configs:
            if x not in new_configs:
                new_configs[x] = round(current_configs[x], 1)
    else:
        for x in candidate_configs:
            new_configs[x] = round((current_configs[x] * (1 - delta_si)), 1)

        for x in current_configs:
            if x not in new_configs:
                new_configs[x] = round(current_configs[x], 1)
    return new_configs, delta_si


def apply_configurations(new_configs):
    """
    This function is used to apply new configurations.json to a system.

    Parameters:
    new_configs (dict or str): The new configurations.json to be applied. If it is a string, it is evaluated as a dictionary.
    system_metadata (dict): The metadata of the system, including information about each container and its replicas.

    Returns:
        None

    Example:
        new_configs = '{"frontend": 0.5}'
        system_metadata = {
            "fronend": {
                "replica": 1/2/3,
                "settings": [
                    {"node": "worker-0", "id": "abcdef"},
                    {"node": "worker-1", "id": "ghijkl"},
                    {"node": "worker-2", "id": "mnopqr"}
                ]
            }
        }
        apply_configurations(new_configs, system_metadata)
    """
    if isinstance(new_configs, str):
        new_configs = eval(new_configs)

    # Loop through each container in the configuration
    for container in new_configs:
        # Retrieve updated system metadata for the container
        settings = retreive_container_metadata(container)

        # Calculate the CPU value for the container
        cpu = round(float(new_configs[container]) / len(settings), 2)

        # Create a list to store the threads that apply the CPU resources
        threads = []

        # Loop through each system info in the metadata
        for info in settings:
            # Print the container name, node, CPU value, and ID
            #print(container, info["node"], cpu, info["id"])
            print(container, info["node"], cpu)

            # Create a thread to apply the CPU resources to the container
            thread = threading.Thread(target=agent.apply_cpu_resource, args=(info["id"], info["node"], int(cpu * 100000)))

            # Add the thread to the list
            threads.append(thread)

        # Start each thread
        for i in threads:
            i.start()

        # Wait for each thread to finish
        for i in threads:
            i.join()


def choose_containers(container_numbers, system_metrics, current_configs):
    """
     This function chooses containers to perform an action on.
     The function will return a dictionary containing the selected container ids and their CPU utilization.

     Args:
         container_numbers (int): The number of containers to be selected
         system_metrics (dict): A dictionary containing system metric information. Each key in the dictionary represents a container id and the value is a dictionary with the following keys:
             - 'throttles': The number of CPU throttles of the container.
             - 'cpu_utilization': The CPU utilization of the container.
         current_configs (dict): A dictionary containing the current configuration of the system. Each key in the dictionary represents a container id and the value is the current CPU allocation of the container.

     Returns:
         dict: A dictionary containing the selected container ids and their CPU utilization.
     """
    candidate_containers = {}
    for x in system_metrics.keys():
        # Skip containers with high number of CPU throttles
        if system_metrics[x]['throttles'] > 0.02:
            continue
        # Skip containers with low CPU utilization
        if current_configs[x] <= 0.3:
            continue
        candidate_containers[x] = system_metrics[x]['cpu_utilization']

    artificial_utils = {}

    # Normalize the CPU utilization of the containers based on their limits
    for x in candidate_containers.keys():
        artificial_utils[x] = candidate_containers[x] / CONTAINER_UTIL_LIMITS[x]
    print("ARTIFICIAL UTILS: ", artificial_utils)

    # If there are not enough containers, return all of them
    if len(candidate_containers) < container_numbers:
        return candidate_containers

    # Scale the CPU utilization of the containers
    util_max = max(artificial_utils.values())
    util_min = min(artificial_utils.values())
    if util_max == util_min:
        for x in artificial_utils:
            scaled = artificial_utils[x] * 60 + 20
            artificial_utils[x] = scaled
    else:
        for x in artificial_utils:
            normalized = (artificial_utils[x] - util_min) / (util_max - util_min)
            scaled = normalized * 60 + 20
            artificial_utils[x] = scaled
    samples = {}

    # Choose the containers with a probability proportional to their scaled CPU utilization
    for x in candidate_containers:
        if random.uniform(5, 95) > artificial_utils[x]:
            samples[x] = candidate_containers[x]
    diff = len(samples) - container_numbers
    keys = list(samples)
    data = {}

    # Select additional containers if necessary
    if diff > 0:
        rng = np.random.default_rng()
        numbers = rng.choice(len(samples), len(samples) - diff, replace=False)
        for i in numbers:
            data[keys[i]] = samples[keys[i]]
        return data
    else:
        return samples


def get_workload_range(rps):
    workload_categories = {
        0: {'min': 0, "max": 100},
        1: {"min": 101, "max": 200},
        2: {"min": 201, "max": 300},
        3: {"min": 301, "max": 400},
        4: {"min": 401, "max": 500},
        5: {"min": 501, "max": 600},
        6: {"min": 601, "max": 700},
        7: {"min": 701, "max": 800},
        8: {"min": 801, "max": 900}
    }
    for category, range_ in workload_categories.items():
        if range_["min"] <= float(rps) <= range_["max"]:
            return category, range_
    return None, None
