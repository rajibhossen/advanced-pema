from algorithm_utils import  apply_configurations
import time
import datetime
from algorithm.db_utils import HistoryDB
from algorithm_data_hr import CONTAINER_LIST, CONTAINER_UTIL_LISTS, CONTAINER_UTIL_LIMITS, CONTAINER_THROTTLE_LIMITS, NUMBER_OF_CONTAINERS, DEFAULT_CONFIGS
from system_metrics.metric_collector import collect_prometheus_data
from system_metrics.collector_backend import get_response_latency, get_request_per_seconds
from system_metrics.metrics_processing import process_prometheus_data, process_configurations
from algorithm_utils import get_workload_range, choose_containers, update_configurations, apply_configurations
from dynamic_thresholds import get_stopping_threshold
from system_metrics.collector_backend import container_replica_and_core


default_configs = {'hotel-reserv-frontend': 4, 'hotel-reserv-geo': 2, 'hotel-reserv-geo-mongo': 3, 'hotel-reserv-profile': 3,
                   'hotel-reserv-profile-mmc': 3, 'hotel-reserv-profile-mongo': 3, 'hotel-reserv-rate': 3,
                   'hotel-reserv-rate-mmc': 3, 'hotel-reserv-rate-mongo': 3, 'hotel-reserv-recommendation': 3,
                   'hotel-reserv-recommendation-mongo': 3, 'hotel-reserv-reservation': 3,
                   'hotel-reserv-reservation-mmc': 3, 'hotel-reserv-reservation-mongo': 3,
                   'hotel-reserv-search': 4, "hotel-reserv-user": 2, "hotel-reserv-user-mongo": 3}

# configs = DEFAULT_CONFIGS
apply_configurations(default_configs)

# start = time.time()
# while True:
#     settings = {}
#     for container in CONTAINER_LIST:
#         core,replica = container_replica_and_core(container)
#         settings[container] = core*replica
#     print(settings)
#     if default_configs == settings:
#         break
#     time.sleep(10)
# print(time.time() - start)
# process these metrics
raw_metrics = collect_prometheus_data(CONTAINER_LIST, duration=120)
system_metrics = process_prometheus_data(raw_metrics, percentile=0.99)

# gather system configuration and metadata such as node, id, settings
system_configs, system_metadata = process_configurations(raw_metrics)
print(system_configs)
