import logging
import os.path
import random
import requests
import os
import time
from datetime import datetime
import sys
import threading


def get_user():
    id = random.randint(0, 500)
    user_name = "Cornell_" + str(id)
    password = ""
    for x in range(10):
        password += str(id)

    return user_name, password


class Requests:
    def __init__(self, logger, uuid):
        self.host = "http://192.168.2.62:30500"

        self.session = requests.Session()
        self.logger = logger
        self.request_uuid = uuid

    def search_hotel(self):
        arrival_time = datetime.now()
        start_time = time.time()

        in_date = random.randint(9, 23)
        out_date = random.randint(in_date + 1, 24)
        in_date_str = str(in_date)
        if in_date <= 9:
            in_date_str = "2015-04-0" + in_date_str
        else:
            in_date_str = "2015-04-" + in_date_str

        out_date_str = str(out_date)
        if out_date <= 9:
            out_date_str = "2015-04-0" + out_date_str
        else:
            out_date_str = "2015-04-" + out_date_str

        lattitude = 38.0235 + (random.randint(0, 481) - 240.5) / 1000.0
        longitude = -122.095 + (random.randint(0, 325) - 325) / 1000.0

        path = "/hotels"
        # headers = {"Content-Type": "application/x-www-form-urlencoded"}
        headers = {}
        body = {"inDate": in_date_str, "outDate": out_date_str, "lat": str(lattitude), "lon": str(longitude)}

        response = self.session.get(url=self.host + path, params=body, headers=headers)

        request_complete_time = datetime.now()
        latency = time.time() - start_time
        to_log = str(arrival_time) + "," + "search_hotels," + str(response.status_code) + "," + str(
            request_complete_time) + "," + str(latency) + "," + self.request_uuid
        self.logger.info(to_log)

    def recommend(self):
        arrival_time = datetime.now()
        start_time = time.time()

        self.coin = random.uniform(0, 1)
        self.req_param = ""
        if self.coin < 0.33:
            self.req_param = "dis"
        elif self.coin < 0.66:
            self.req_param = "rate"
        else:
            self.req_param = "price"

        lattitude = 38.0235 + (random.randint(0, 481) - 240.5) / 1000.0
        longitude = -122.095 + (random.randint(0, 325) - 325) / 1000.0

        path = "/recommendations"
        # headers = {"Content-Type": "application/x-www-form-urlencoded"}
        headers = {}
        body = {"require": self.req_param, "lat": str(lattitude), "lon": str(longitude)}

        response = self.session.get(url=self.host + path, params=body, headers=headers)

        request_complete_time = datetime.now()
        response_time = time.time() - start_time
        to_log = str(arrival_time) + "," + "recommendations," + str(response.status_code) + "," + str(
            request_complete_time) + "," + str(response_time) + "," + self.request_uuid
        self.logger.info(to_log)

    def reserve(self):
        arrival_time = datetime.now()
        start_time = time.time()

        in_date = random.randint(9, 23)
        out_date = in_date + random.randint(1, 5)

        in_date_str = str(in_date)
        if in_date <= 9:
            in_date_str = "2015-04-0" + in_date_str
        else:
            in_date_str = "2015-04-" + in_date_str

        out_date_str = str(out_date)
        if out_date <= 9:
            out_date_str = "2015-04-0" + out_date_str
        else:
            out_date_str = "2015-04-" + out_date_str

        hotel_id = str(random.randint(1, 80))
        user_id, password = get_user()
        cust_name = user_id

        num_rooms = "1"

        lattitude = 38.0235 + (random.randint(0, 481) - 240.5) / 1000.0
        longitude = -122.095 + (random.randint(0, 325) - 325) / 1000.0

        path = "/reservation"
        # headers = {"Content-Type": "application/x-www-form-urlencoded"}
        headers = {}
        body = {"inDate": in_date_str, "outDate": out_date_str, "lat": str(lattitude), "lon": str(longitude),
                "hotelId": hotel_id, "customerName": cust_name, "username": user_id, "password": password,
                "number": num_rooms}

        response = self.session.post(url=self.host + path, params=body, headers=headers)

        request_complete_time = datetime.now()
        response_time = time.time() - start_time
        to_log = str(arrival_time) + "," + "reserve," + str(response.status_code) + "," + str(
            request_complete_time) + "," + str(response_time) + "," + self.request_uuid
        self.logger.info(to_log)

    def login(self):
        arrival_time = datetime.now()
        start_time = time.time()

        username, password = get_user()

        path = "/user"
        # headers = {"Content-Type": "application/x-www-form-urlencoded"}
        headers = {}
        body = {"username": username, "password": password}

        response = self.session.get(url=self.host + path, params=body, headers=headers)

        request_complete_time = datetime.now()
        response_time = time.time() - start_time
        to_log = str(arrival_time) + "," + "login," + str(response.status_code) + "," + str(
            request_complete_time) + "," + str(response_time) + "," + self.request_uuid
        self.logger.info(to_log)

    def perform_task(self, name):
        task = getattr(self, name)
        task()


def hr_task_types(logger, uuid):
    # request_obj = Requests(logger, uuid)
    # search_ratio = 0.4
    # recommend_ratio = 0.3
    # user_ratio = 0.15
    # reserve_ratio = 0.15

    # coin_toss = random.uniform(0, 1)
    # if coin_toss < search_ratio:
    #     task_to_perform = 'search_hotel'
    # elif coin_toss < search_ratio + recommend_ratio:
    #     task_to_perform = 'recommend'
    # elif coin_toss < search_ratio + recommend_ratio + user_ratio:
    #     task_to_perform = 'login'
    # else:
    #     task_to_perform = 'reserve'
    task_type1 = ["search_hotel", "recommend"]
    task_type2 = ["login", "search_hotel"]
    task_type3 = ["recommend", "login"]
    task_type4 = ["login", "recommend", "search_hotel"]

    tasks = random.choice([task_type1, task_type2, task_type3, task_type4])
    req_obj = Requests(logger, uuid)
    for task in tasks:
        req_obj.perform_task(task)
    # request_obj.perform_task(task_to_perform)
