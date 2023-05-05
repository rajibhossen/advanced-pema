import json
import math
from pathlib import Path
import paramiko
import time
import numpy as np

from system_metrics.collector_backend import get_cpu_utilization, container_replica_and_core, gauge_metrics, \
    counter_metrics, get_request_per_seconds, get_response_latency
from system_metrics.jaeger_tracing import jaeger_tracing
from system_metrics.metrics_processing import process_prometheus_data, process_jaeger_data


memory_gauge_metrics = ["container_memory_usage_bytes", "container_memory_failcnt"]
cpu_gauge_metrics = ['container_processes', 'container_cpu_load_average_10s', 'container_threads']
# network_metrics = ["container_network_receive_bytes_total", 'container_network_receive_errors_total',
#                    "container_network_transmit_errors_total", "container_network_transmit_bytes_total"]
DISK_METRICS = ["container_fs_io_time_seconds_total", "container_fs_read_seconds_total",
                "container_fs_write_seconds_total"]
# TIME_SCALE = "[1m]"

jaeger_containers = ['frontend', 'geo', 'geo-mongo', 'profile', 'profile-mmc', 'profile-mongo', 'rate', 'rate-mmc',
                     'rate-mongo', 'recommendation', 'recommendation-mongo', 'reservation', 'reservation-mmc',
                     'reservation-mongo', 'search', 'user', 'user-mongo']


def collect_prometheus_data(containers, duration=30):
    metric_data = {}
    for container in containers:
        if container not in metric_data.keys():
            metric_data[container] = {}

        # collect cpu related metrics
        if "cpu" not in metric_data[container]:
            metric_data[container]["cpu"] = {}

        settings, usage = get_cpu_utilization(container, TIME_SCALE=duration)
        cpu_core, replica = container_replica_and_core(container)
        throttles = counter_metrics('container_cpu_cfs_throttled_seconds_total', container, TIME_SCALE=duration)

        metric_data[container]["cpu_core"] = cpu_core
        metric_data[container]["replica"] = replica
        metric_data[container]["settings"] = settings
        metric_data[container]["cpu"]["usage"] = usage
        metric_data[container]["cpu"]["throttle_time"] = throttles

        for gauge_met in cpu_gauge_metrics:
            data = gauge_metrics(gauge_met, container, TIME_SCALE=duration)
            metric_data[container]['cpu'][gauge_met] = [eval(i) for i in data]

        if "memory" not in metric_data[container]:
            metric_data[container]["memory"] = {}
        for mem_gauge in memory_gauge_metrics:
            data = gauge_metrics(mem_gauge, container, TIME_SCALE=duration)
            metric_data[container]['memory'][mem_gauge] = [eval(i) for i in data]

        # if "network" not in metric_data[container]:
        #     metric_data[container]['network'] = {}
        # for net_metrics in network_metrics:
        #     data = counter_metrics(net_metrics, container, TIME_SCALE=time_scale)
        #     metric_data[container]['network'][net_metrics] = data

        if 'disk' not in metric_data[container]:
            metric_data[container]['disk'] = {}
        for disk_mets in DISK_METRICS:
            data = counter_metrics(disk_mets, container, TIME_SCALE=duration)
            metric_data[container]['disk'][disk_mets] = data
    return metric_data


def collect_jaeger_data(time):
    final_traces = {}
    for c in jaeger_containers:
        result = jaeger_tracing(c, time)
        # print(result)
        for key, val in result.items():
            if key not in final_traces:
                final_traces[key] = val
    return final_traces


# def get_rps_and_latency(container, duration=30, percentile=0.95):
#     latency = get_response_latency(container, duration, percentile)
#     rps = get_request_per_seconds(container, duration)
#     return float(rps), float(latency)

#
# if __name__ == '__main__':
#     while True:
#         rps, latency = get_rps_and_latency(container='frontend', duration=60, percentile=0.99)
#         print(rps, latency)
#         time.sleep(5)
#
# data = collect_prometheus_data(time_scale=1)
# print(data)
# print(process_prometheus_data(data))
# jaeger_data = collect_jaeger_data(60)
# jaeger_data = process_jaeger_data(jaeger_data)
# print(jaeger_data)
