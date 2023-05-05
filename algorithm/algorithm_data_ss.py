EXPERIMENT_TIME = 120  # seconds
THROTTLE_PERCENTAGE = 0.00085  # 1%
default = 10

CONTAINER_LIST = ['carts', 'catalogue', 'front-end', 'orders', 'payment', 'shipping', 'user']

DEFAULT_CONFIGS = {"carts": 5.0, "catalogue": 5.0, "front-end": 5.0, "orders": 5.0, "payment": 5.0, "shipping": 5.0,
                   "user": 5.0}

CONTAINER_UTIL_LIMITS = {"carts": default, "catalogue": default, "front-end": default, "orders": default,
                         "payment": default, "shipping": default, "user": default}

CONTAINER_THROTTLE_LIMITS = {"carts": 0, "catalogue": 0, "front-end": 0, "orders": 0, "payment": 0, "shipping": 0,
                             "user": 0}

CONTAINER_UTIL_LISTS = {"carts": [], "catalogue": [], "front-end": [], "orders": [], "payment": [], "shipping": [],
                        "user": []}

NUMBER_OF_CONTAINERS = len(CONTAINER_LIST)
