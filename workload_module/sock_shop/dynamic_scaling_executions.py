import os
import time

configurations = {"frontend": {"cpu": 1, "replica": 3},
                  "geo": {"cpu": 2.0, "replica": 1},
                  "mongodb-geo": {"cpu": 1.0, "replica": 1},
                  "profile": {"cpu": 2.0, "replica": 1},
                  "memcached-profile": {"cpu": 1.0, "replica": 1},
                  "mongodb-profile": {"cpu": 1.0, "replica": 1},
                  "rate": {"cpu": 2.0, "replica": 1},
                  "memcached-rate": {"cpu": 1.0, "replica": 1},
                  "mongodb-rate": {"cpu": 1.0, "replica": 1},
                  "recommendation": {"cpu": 2.0, "replica": 1},
                  "mongodb-recommendation": {"cpu": 2.0, "replica": 1},
                  "reservation": {"cpu": 2.0, "replica": 2},
                  "memcached-reserve": {"cpu": 2.0, "replica": 1},
                  "mongodb-reservation": {"cpu": 2.0, "replica": 1},
                  "search": {"cpu": 2.0, "replica": 1},
                  "user": {"cpu": 2.0, "replica": 1},
                  "mongodb-user": {"cpu": 2.0, "replica": 1}}


def apply_executions():
    for container in configurations.keys():
        # apply horizontal scaling
        horizontal_command = 'kubectl scale deployment ' + container + ' --replicas=' + str(
            configurations[container]['replica'])
        print(horizontal_command)
        os.system(horizontal_command)

        # apply vertical scaling
        vertical_command = 'kubectl set resources deployment ' + container + ' --limits=cpu=' + str(
            configurations[container]['cpu']) + ' --requests=cpu=' + str(configurations[container]['cpu'])
        # print(vertical_command)
        os.system(vertical_command)
        # break
        time.sleep(2)


apply_executions()
