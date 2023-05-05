
EXPERIMENT_TIME = 120  # seconds
THROTTLE_PERCENTAGE = 0.00085  # 1%
default = 10

CONTAINER_LIST = ['hotel-reserv-frontend','hotel-reserv-geo','hotel-reserv-geo-mongo', 'hotel-reserv-profile',
                   'hotel-reserv-profile-mmc', 'hotel-reserv-profile-mongo', 'hotel-reserv-rate',
                   'hotel-reserv-rate-mmc', 'hotel-reserv-rate-mongo', 'hotel-reserv-recommendation',
                   'hotel-reserv-recommendation-mongo', 'hotel-reserv-reservation',
                   'hotel-reserv-reservation-mmc', 'hotel-reserv-reservation-mongo',
                   'hotel-reserv-search', "hotel-reserv-user", "hotel-reserv-user-mongo"]

DEFAULT_CONFIGS = {'hotel-reserv-frontend': 4, 'hotel-reserv-geo': 2, 'hotel-reserv-geo-mongo': 3, 'hotel-reserv-profile': 3,
                   'hotel-reserv-profile-mmc': 3, 'hotel-reserv-profile-mongo': 3, 'hotel-reserv-rate': 3,
                   'hotel-reserv-rate-mmc': 3, 'hotel-reserv-rate-mongo': 3, 'hotel-reserv-recommendation': 3,
                   'hotel-reserv-recommendation-mongo': 3, 'hotel-reserv-reservation': 3,
                   'hotel-reserv-reservation-mmc': 3, 'hotel-reserv-reservation-mongo': 3,
                   'hotel-reserv-search': 4, "hotel-reserv-user": 2, "hotel-reserv-user-mongo": 3}

CONTAINER_UTIL_LIMITS = {'hotel-reserv-frontend': default, 'hotel-reserv-geo': default, 'hotel-reserv-geo-mongo': default, 'hotel-reserv-profile': default,
                   'hotel-reserv-profile-mmc': default, 'hotel-reserv-profile-mongo': default, 'hotel-reserv-rate': default,
                   'hotel-reserv-rate-mmc': default, 'hotel-reserv-rate-mongo': default, 'hotel-reserv-recommendation': default,
                   'hotel-reserv-recommendation-mongo': default, 'hotel-reserv-reservation': default,
                   'hotel-reserv-reservation-mmc': default, 'hotel-reserv-reservation-mongo': default,
                   'hotel-reserv-search': default, "hotel-reserv-user": default, "hotel-reserv-user-mongo": default}

CONTAINER_THROTTLE_LIMITS = {'hotel-reserv-frontend': 0, 'hotel-reserv-geo': 0, 'hotel-reserv-geo-mongo': 0, 'hotel-reserv-profile': 0,
                   'hotel-reserv-profile-mmc': 0, 'hotel-reserv-profile-mongo': 0, 'hotel-reserv-rate': 0,
                   'hotel-reserv-rate-mmc': 0, 'hotel-reserv-rate-mongo': 0, 'hotel-reserv-recommendation': 0,
                   'hotel-reserv-recommendation-mongo': 0, 'hotel-reserv-reservation': 0,
                   'hotel-reserv-reservation-mmc': 0, 'hotel-reserv-reservation-mongo': 0,
                   'hotel-reserv-search': 0, "hotel-reserv-user": 0, "hotel-reserv-user-mongo": 0}

CONTAINER_UTIL_LISTS = {'hotel-reserv-frontend': [], 'hotel-reserv-geo': [], 'hotel-reserv-geo-mongo': [], 'hotel-reserv-profile': [],
                   'hotel-reserv-profile-mmc': [], 'hotel-reserv-profile-mongo': [], 'hotel-reserv-rate': [],
                   'hotel-reserv-rate-mmc': [], 'hotel-reserv-rate-mongo': [], 'hotel-reserv-recommendation': [],
                   'hotel-reserv-recommendation-mongo': [], 'hotel-reserv-reservation': [],
                   'hotel-reserv-reservation-mmc': [], 'hotel-reserv-reservation-mongo': [],
                   'hotel-reserv-search': [], "hotel-reserv-user": [], "hotel-reserv-user-mongo": []}

NUMBER_OF_CONTAINERS = len(CONTAINER_LIST)