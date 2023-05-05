import numpy as np
import json


def average(items):
    if items:
        res = [float(i) for i in items]
        return sum(res) / len(res)
    else:
        return 0


def process_prometheus_data(metric_data, percentile=95):
    # print(metric_data)
    processed_data = {}
    for key in metric_data.keys():
        processed_data[key] = {}
        cpu_usage = metric_data[key]['cpu']['usage']
        # print(key, metric_data[key])

        if cpu_usage:
            cpu_utilization = average(cpu_usage) / (metric_data[key]['cpu_core'] * metric_data[key]['replica'])
        else:
            cpu_utilization = 0

        processed_data[key]['cpu_utilization'] = cpu_utilization * 100
        processed_data[key]['throttles'] = average(metric_data[key]['cpu']['throttle_time'])
        processed_data[key]['processes'] = max(metric_data[key]['cpu']['container_processes'])
        processed_data[key]['load_average'] = average(metric_data[key]['cpu']['container_cpu_load_average_10s'])
        processed_data[key]['threads'] = average(metric_data[key]['cpu']['container_threads'])

        # temporary, calculate memory utilization with memory limits
        processed_data[key]['memory_utilization'] = average(metric_data[key]['memory']['container_memory_usage_bytes'])

        processed_data[key]['io_time'] = average(metric_data[key]['disk']['container_fs_io_time_seconds_total'])
        processed_data[key]['read_seconds'] = average(metric_data[key]['disk']['container_fs_read_seconds_total'])
        processed_data[key]['write_seconds'] = average(metric_data[key]['disk']['container_fs_write_seconds_total'])

    return processed_data


def process_configurations(metric_data):
    configs = {}
    metadata = {}

    for key in metric_data.keys():
        # print(key, metric_data[key]['cpu_core'], metric_data[key]['replica'])
        configs[key] = metric_data[key]['cpu_core'] * metric_data[key]['replica']
        metadata[key] = {'settings': metric_data[key]['settings'], 'replica': len(metric_data[key]['settings'])}
    return configs, metadata


def process_jaeger_data(metric_data, percentile=95):
    microservices = {}
    for trace in metric_data.keys():
        for stat in metric_data[trace]['stats'].keys():
            if stat not in microservices.keys():
                microservices[stat] = {}
            for value in metric_data[trace]['stats'][stat].keys():
                if value in microservices[stat].keys():
                    microservices[stat][value].append(metric_data[trace]['stats'][stat][value])
                else:
                    microservices[stat][value] = [metric_data[trace]['stats'][stat][value]]

    for service in microservices.keys():
        for stat in microservices[service].keys():
            if stat == 'count':
                microservices[service][stat] = sum(microservices[service][stat])
            else:
                microservices[service][stat] = np.percentile(np.array(microservices[service][stat]), percentile)

    return microservices
