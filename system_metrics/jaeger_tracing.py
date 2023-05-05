import sys
import datetime
import requests

from system_metrics.trace_classes import Span, Trace, SpanReference
from system_metrics.trace_statistics import calculate_content

JAEGER_URL = "http://192.168.2.62:30314"


def process_trace_data(trace_data):
    trace_lists = {}
    for trace in trace_data:
        # print(trace)
        # trace = trace_data[x]
        trace_id = trace["traceID"]
        trace_start_time = sys.maxsize
        trace_end_time = 0
        trace["spans"] = [span for span in trace["spans"] if span["startTime"]]
        spans = trace["spans"]
        process = trace["processes"]  # for jaeger
        for span in spans:
            start_time = span["startTime"]
            duration = span["duration"]

            if start_time < trace_start_time:
                trace_start_time = start_time

            if start_time + duration > trace_end_time:
                trace_end_time = start_time + duration

        trace_duration = round(((trace_end_time - trace_start_time) / 1000.0) * 100, 2) / 100  # converting to ms

        for span in spans:
            span["service_name"] = process[span["processID"]]["serviceName"]  # for jaeger
            # span["service_name"] = span["process"]["serviceName"] # for elasticsearch
            span["relativeStartTime"] = span["startTime"] - trace_start_time
            span["hasChildren"] = True
        # print(spans)
        trace_statistics = {}
        for span in spans:
            if span["service_name"] in trace_statistics.keys():
                trace_statistics[span["service_name"]] = calculate_content(span, spans,
                                                                           trace_statistics[span["service_name"]])
            else:
                trace_statistics[span["service_name"]] = {}
                trace_statistics[span["service_name"]]["count"] = 0
                trace_statistics[span["service_name"]]["total"] = 0
                trace_statistics[span["service_name"]]["min"] = span["duration"]
                trace_statistics[span["service_name"]]["max"] = 0
                trace_statistics[span["service_name"]]["selfMin"] = span["duration"]
                trace_statistics[span["service_name"]]["selfMax"] = 0
                trace_statistics[span["service_name"]]["selfTotal"] = 0
                trace_statistics[span["service_name"]] = calculate_content(span, spans,
                                                                           trace_statistics[span["service_name"]])
        for stats in trace_statistics:
            trace_statistics[stats]["min"] = round((trace_statistics[stats]["min"] / 1000) * 100) / 100
            trace_statistics[stats]["max"] = round((trace_statistics[stats]["max"] / 1000) * 100) / 100
            trace_statistics[stats]["total"] = round((trace_statistics[stats]["total"] / 1000) * 100) / 100
            if trace_statistics[stats]["count"]:
                trace_statistics[stats]["avg"] = trace_statistics[stats]["total"] / trace_statistics[stats]["count"]
                trace_statistics[stats]["selfAvg"] = trace_statistics[stats]["selfTotal"] / trace_statistics[stats][
                    "count"]
            trace_statistics[stats]["selfMin"] = round((trace_statistics[stats]["selfMin"] / 1000) * 100) / 100
            trace_statistics[stats]["selfMax"] = round((trace_statistics[stats]["selfMax"] / 1000) * 100) / 100
            trace_statistics[stats]["selfTotal"] = round((trace_statistics[stats]["selfTotal"] / 1000) * 100) / 100
            trace_statistics[stats]["STinDuration"] = (trace_statistics[stats]["selfTotal"] / trace_duration) * 100
        # print(json.dumps(trace_statistics))
        trace_formatted_data = {"trace_id": trace_id,
                                "duration": trace_duration,
                                "start_time": trace_start_time,
                                "end_time": trace_end_time,
                                # "spans": trace["spans"],
                                "stats": trace_statistics}
        trace_lists[trace_id] = trace_formatted_data
    return trace_lists


def jaeger_tracing(container_name, limit):
    time_delta = limit  # in minutes
    end_timestamp = datetime.datetime.now().timestamp()
    start_timestamp = datetime.datetime.now() - datetime.timedelta(minutes=time_delta)
    start_timestamp = start_timestamp.timestamp()
    # print(start_timestamp, end_timestamp)
    start_date = datetime.datetime.fromtimestamp(start_timestamp).strftime('%s') + '000000'
    end_date = datetime.datetime.fromtimestamp(end_timestamp).strftime('%s') + '000000'

    # service_name = 'ts-travel-service'
    uri = JAEGER_URL + "/api/traces?end=" + end_date + "&limit=&lookback=custom&maxDuration&minDuration&service=" + container_name + "&start=" + start_date
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}
    #print(uri)
    traces = requests.get(url=uri, headers=headers)
    trace_data = traces.json()
    # print(json.dumps(trace_data))
    trace_stats = process_trace_data(trace_data["data"])
    #print(trace_stats)
    return trace_stats
    # print(json.dumps(trace_stats))

