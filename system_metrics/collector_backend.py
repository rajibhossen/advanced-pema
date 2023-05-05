import json
import time
from numpy import median, percentile
import requests

BASE_URL = "http://192.168.2.62:30004"
BASE_QUERY = BASE_URL + "/api/v1/query?query="
# METRIC_DATA = {}

metrics = []


def get_json_response(metric_name, container_name, duration):

    metric_url = metric_name + "{container=~\"" + container_name+"\"}"

    if duration:
        time_identifier = 's'
        # if duration >= 60:
        #     duration = int(duration / 60)
        #     time_identifier = 'm'
        query_url = BASE_URL + "/api/v1/query?query=" + metric_url + "[" + str(duration) + time_identifier + "]"
    else:
        query_url = BASE_URL + "/api/v1/query?query=" + metric_url

    results = requests.get(url=query_url)
    query_data = results.json()
    return query_data


def metrics_with_rate(metric_name, container_name, duration):
    # if duration >= 60:
    #     duration = int(duration/60)
    #     time_identifier = 'm'
    # else:
    time_identifier = 's'

    metric_name = '%s{container="%s"}' % (metric_name, container_name)
    query = "rate(%s[%d%s])" % (metric_name, duration, time_identifier)
    query_url = f"{BASE_URL}/api/v1/query?query={query}"
    # print(query_url)
    results = requests.get(url=query_url)
    query_data = results.json()
    return query_data


def get_cpu_utilization(container, TIME_SCALE):
    cpu_util = metrics_with_rate("container_cpu_usage_seconds_total", container, duration=TIME_SCALE)
    # holds cpu usage for all replicas
    cpu_usage_each = []
    container_settings = []
    # print(cpu_util)
    for data in cpu_util["data"]["result"]:
        # keep id and node of each replicas
        container_settings.append(
            {"id": data["metric"]["id"], "node": data["metric"]["instance"], "name": data["metric"]["name"]})

        # for i in range(len(data["values"]) - 1):
        #     cpu_time_diff = float(data["values"][i + 1][1]) - float(data["values"][i][1])
        #     time_diff = float(data["values"][i + 1][0]) - float(data["values"][i][0])
        #     cpu_usage_each.append(cpu_time_diff / time_diff)  # calculate rate of change for each points
        cpu_usage_each.append(data['value'][1])
    return container_settings, cpu_usage_each


def counter_metrics(metric_name, container, TIME_SCALE):
    result = metrics_with_rate(metric_name, container, duration=TIME_SCALE)
    final_data = []
    # num_of_points = 0
    # for data in result["data"]["result"]:
    #     for i in range(len(data["values"]) - 1):
    #         rate_of_change = float(data["values"][i + 1][1]) - float(data["values"][i][1])
    #         time_diff = float(data["values"][i + 1][0]) - float(data["values"][i][0])
    #         final_data.append(rate_of_change / time_diff)
    for data in result['data']['result']:
        final_data.append(data['value'][1])
    return final_data


def container_replica_and_core(container):

    cpu_quota = get_json_response("container_spec_cpu_quota", container, duration=60)
    quota, period, cpu_core, replica = None, None, None, 1

    if cpu_quota['data']['result']:
        replica = len(cpu_quota['data']['result'])
        result_length = len(cpu_quota["data"]["result"][0]["values"])
        quota = cpu_quota["data"]["result"][0]["values"][result_length-1][1]

    # cpu_period = get_json_response("container_spec_cpu_period", container, duration=120)
    # if cpu_period['data']['result']:
    #     period = cpu_period["data"]["result"][0]["values"][0][1]
    period = 100000
    if quota and period:
        cpu_core = (float(quota) / float(period))  # calculate total core of a container
        return cpu_core, replica


def gauge_metrics(metric_name, container, TIME_SCALE):
    result = get_json_response(metric_name, container, duration=TIME_SCALE)
    final_data = []
    for data in result['data']['result']:
        for value in data['values']:
            final_data.append(value[1])
    return final_data


def get_request_per_seconds(container_name, duration=60):
    # if duration >= 60:
    #     duration = int(duration/60)
    #     time_identifier = 'm'
    # else:
    time_identifier = 's'

    duration = str(duration)
    metric_name = 'request_total{deployment="%s",direction="inbound"}' % container_name
    query = "sum(irate(%s[%s%s]))" % (metric_name, duration,time_identifier)
    query_url = f"{BASE_URL}/api/v1/query?query={query}"

    results = requests.get(url=query_url)
    query_data = results.json()

    # result format - {'status': 'success', 'data': {'resultType': 'vector', 'result': [{'metric': {}, 'value': [1675128333.444, '4.6000000000000005']}]}}
    rps = query_data['data']['result'][0]['value'][1]
    return rps


def get_response_latency(container_name, duration=60, percentile=0.95):
    duration = str(duration)
    metric_url = f"response_latency_ms_bucket{{deployment=\"{container_name}\",direction=\"inbound\"}}"
    query_url = f"{BASE_URL}/api/v1/query?query=histogram_quantile({percentile},sum(rate({metric_url}[{duration}s])) by (le,deployment))"
    results = requests.get(url=query_url)
    query_data = results.json()
    if query_data['data']['result']:
        percentile_response = query_data['data']['result'][0]['value'][1]
        return percentile_response
    else:
        return None


def retreive_container_metadata(container_name):
    cpu_util = get_json_response("container_spec_cpu_period", container_name, duration=None)
    container_id = []
    for data in cpu_util["data"]["result"]:
        # keep id and node of each replicas
        container_id.append({"id": data["metric"]["id"], "node": data["metric"]["instance"]})
    return container_id

# def get_response(container_name, duration=60, percentile=0.95):
#     if duration >= 60:
#         duration = int(duration/60)
#         time_identifier = 'm'
#     else:
#         time_identifier = 's'
#
#     duration = str(duration)
#     metric_url = f"response_latency_ms_bucket{{deployment=\"{container_name}\",direction=\"inbound\"}}"
#     query_url = f"{BASE_URL}/api/v1/query?query=({metric_url}[{duration}{time_identifier}])"
#     results = requests.get(url=query_url)
#     query_data = results.json()
#     print(query_data)
    # percentile_response = query_data['data']['result'][0]['value'][1]
    # return percentile_response

# [None, None, '35.76795035812437', '34.5488091208522', '38.647754019253235', '44.12180902472307', '42.52226891148376', '42.51013125790861', '40.966979698518735', '40.636407221907575', '39.6724144865923', '40.02658030815189']
# ['39.04509803921553', '35.82830188679248', '36.468000000000075', '40.353846153846106', '41.333333333333655', '37.40487804878038', '37.99183673469361', '40.83255813953503', '48.20454545454548', '43.146874999999795', '37.01698113207548', '39.100000000000136']
#
# progressive = []
# iterative = []
# i = 10
# time_taken_iterative = []
# time_taken_progressive = []
# while i < 130:
#     start = time.time()
#     iterative_latency = get_response_latency(container_name='frontend', duration=30, percentile=0.99)
#     time_taken_iterative.append(time.time() - start)
#
#     # start = time.time()
#     # progressive_latency = get_response_latency(container_name='frontend', duration=i, percentile=0.99)
#     # time_taken_progressive.append(time.time() - start)
#     # if progressive_latency:
#     #     progressive.append(float(progressive_latency))
#     # else:
#     #     progressive.append(0)
#     # iterative.append((float(iterative_latency)))
#     #print(i, progressive_latency, iterative_latency)
#     i += 10
#     time.sleep(10)
# # print(progressive)
# # print(iterative)
# print(time_taken_iterative)
# print(time_taken_progressive)
