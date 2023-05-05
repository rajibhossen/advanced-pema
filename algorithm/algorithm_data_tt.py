
EXPERIMENT_TIME = 120  # seconds
THROTTLE_PERCENTAGE = 0.00085  # 1%
default = 10

CONTAINER_LIST = ['ts-assurance-service', 'ts-auth-service', 'ts-basic-service', 'ts-config-service',
                  'ts-consign-price-service', 'ts-consign-service', 'ts-contacts-service', 'ts-food-map-service',
                  'ts-food-service', 'ts-order-other-service', 'ts-order-service', 'ts-preserve-other-service',
                  'ts-preserve-service', 'ts-price-service', 'ts-route-plan-service', 'ts-route-service',
                  'ts-seat-service', 'ts-security-service', 'ts-station-service', 'ts-ticketinfo-service',
                  'ts-train-service', 'ts-travel-plan-service', 'ts-travel-service', 'ts-travel2-service',
                  'ts-user-service']

DEFAULT_CONFIGS = {'ts-assurance-service': 2.0, 'ts-basic-service': 4, 'ts-config-service': 2.5,
                   'ts-consign-price-service': 2, 'ts-consign-service': 2, 'ts-contacts-service': 2.5,
                   'ts-food-map-service': 2, 'ts-food-service': 2.5, 'ts-auth-service': 10.5,
                   'ts-order-other-service': 2.5, 'ts-order-service': 5,
                   'ts-preserve-other-service': 2, 'ts-preserve-service': 4, 'ts-price-service': 2.5,
                   'ts-route-plan-service': 2, 'ts-route-service': 4, 'ts-seat-service': 5, 'ts-security-service': 5,
                   'ts-user-service': 2,
                   'ts-station-service': 5, 'ts-ticketinfo-service': 3, 'ts-train-service': 2,
                   'ts-travel2-service': 5, 'ts-travel-plan-service': 2, 'ts-travel-service': 5}

container_limits = {'ts-assurance-service': default, 'ts-basic-service': default, 'ts-config-service': default,
                    'ts-consign-price-service': default, 'ts-consign-service': default, 'ts-contacts-service': default,
                    'ts-food-map-service': default, 'ts-food-service': default, 'ts-auth-service': default,
                    'ts-order-other-service': default, 'ts-order-service': default,
                    'ts-preserve-other-service': default, 'ts-preserve-service': default, 'ts-price-service': default,
                    'ts-route-plan-service': default, 'ts-route-service': default, 'ts-seat-service': default,
                    'ts-security-service': default,
                    'ts-user-service': default,
                    'ts-station-service': default, 'ts-ticketinfo-service': default, 'ts-train-service': default,
                    'ts-travel2-service': default, 'ts-travel-plan-service': default, 'ts-travel-service': default}

CONTAINER_UTIL_LIMITS = {'hotel-reserv-frontend': default, 'hotel-reserv-geo': default, 'hotel-reserv-geo-mongo': default, 'hotel-reserv-profile': default,
                   'hotel-reserv-profile-mmc': default, 'hotel-reserv-profile-mongo': default, 'hotel-reserv-rate': default,
                   'hotel-reserv-rate-mmc': default, 'hotel-reserv-rate-mongo': default, 'hotel-reserv-recommendation': default,
                   'hotel-reserv-recommendation-mongo': default, 'hotel-reserv-reservation': default,
                   'hotel-reserv-reservation-mmc': default, 'hotel-reserv-reservation-mongo': default,
                   'hotel-reserv-search': default, "hotel-reserv-user": default, "hotel-reserv-user-mongo": default}

CONTAINER_THROTTLE_LIMITS = {'ts-assurance-service': 0, 'ts-basic-service': 0, 'ts-config-service': 0,
                             'ts-consign-price-service': 0, 'ts-consign-service': 0, 'ts-contacts-service': 0,
                             'ts-food-map-service': 0, 'ts-food-service': 0, 'ts-auth-service': 0,
                             'ts-order-other-service': 0, 'ts-order-service': 0,
                             'ts-preserve-other-service': 0, 'ts-preserve-service': 0, 'ts-price-service': 0,
                             'ts-route-plan-service': 0, 'ts-route-service': 0, 'ts-seat-service': 0,
                             'ts-security-service': 0,
                             'ts-user-service': 0,
                             'ts-station-service': 0, 'ts-ticketinfo-service': 0, 'ts-train-service': 0,
                             'ts-travel2-service': 0, 'ts-travel-plan-service': 0, 'ts-travel-service': 0}

CONTAINER_UTIL_LISTS = {'ts-assurance-service': [], 'ts-basic-service': [], 'ts-config-service': [],
                       'ts-consign-price-service': [], 'ts-consign-service': [], 'ts-contacts-service': [],
                       'ts-food-map-service': [], 'ts-food-service': [], 'ts-auth-service': [],
                       'ts-order-other-service': [], 'ts-order-service': [],
                       'ts-preserve-other-service': [], 'ts-preserve-service': [], 'ts-price-service': [],
                       'ts-route-plan-service': [], 'ts-route-service': [], 'ts-seat-service': [],
                       'ts-security-service': [],
                       'ts-user-service': [],
                       'ts-station-service': [], 'ts-ticketinfo-service': [], 'ts-train-service': [],
                       'ts-travel2-service': [], 'ts-travel-plan-service': [], 'ts-travel-service': []}

NUMBER_OF_CONTAINERS = len(CONTAINER_LIST)