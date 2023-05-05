import time
import threading
import sys
from hotel_reservation.api_calls import hr_task_types
import random
import logging
from datetime import datetime

total_user = 0


def setup_logger(file_name):
    #dir_path = os.path.dirname(os.path.realpath(__file__))
    #handler = logging.FileHandler(os.path.join(dir_path, "log_data/" + file_name + ".log"))
    handler = logging.FileHandler(file_name)
    handler.setFormatter(logging.Formatter('%(message)s'))
    logger = logging.getLogger("Requests logger")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.info("arrival_time,service,status_code,response_time,latency,user")
    return logger


def start_load_test(logger, lambd, runtime):
    end_time = time.time() + runtime
    total_user = 0
    while time.time() < end_time:
        thread = threading.Thread(target=hr_task_types, args=(logger, str(total_user)))
        thread.start()
        next_arrival = random.expovariate(1 / lambd)
        time.sleep(next_arrival / 1000.0)
        total_user += 1
        # print(next_arrival)

    main_thread = threading.current_thread()
    for x in threading.enumerate():
        if x is main_thread:
            continue
        x.join()
    return total_user


if __name__ == '__main__':
    arrival_rate = int(sys.argv[1])
    runtime = int(sys.argv[2])
    file_name = sys.argv[3]
    logger = setup_logger(file_name)
    start_time = time.time()
    print("Start Testing with arrival rate - %s ms, runtime--%s s, log file %s" % (arrival_rate, runtime, file_name))

    total_user = start_load_test(logger, arrival_rate, runtime)

    print("Finish Testing at %s, Total User Spawned - %s" % (datetime.now(), total_user))
    print("Elapsed Time: ", time.time() - start_time)


