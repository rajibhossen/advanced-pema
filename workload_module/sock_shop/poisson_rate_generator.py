import numpy as np
from scipy.interpolate import interp1d


def poisson_rate_hr(requested_rps):
    # poisson = 32684 * requests**(-1*1.049)
    rps = [612, 534.98, 485.32, 435.65, 384.7, 355.12, 341.03, 310.12, 299.78, 274.06, 255.08, 240.47, 227.75, 222.22, 210.15, 201.03, 190.83, 186]
    poisson = [35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105, 110, 115, 120]
    #
    x = np.array(rps)
    y = np.array(poisson)
    f = interp1d(x, y)
    poisson = f(np.array(requested_rps))
    return int(poisson)


def poisson_rate_sock_shop(request):

    # poisson = 48901 * requests**(-1*1.053)
    rps = [1327.87, 1138.9, 1009, 862.6, 803.8, 726.7, 666.9, 624.4, 574.2, 530.4, 493.9, 472.2, 435.9, 427, 408.7, 364.4, 305.0, 280.6, 254.1, 214.5,
           191.1, 186.6, 156.7, 153.9, 143.6, 138.7, 119.3, 99.4, 88.6, 79.6, 74.4, 70.5, 67.1, 60.6, 60.7, 59.3]
    poisson = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 120, 140, 160, 180, 200, 220, 240,
               260, 280, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800]
    x = np.array(rps)
    y = np.array(poisson)
    f = interp1d(x, y)
    poisson = f(np.array(request))
    return int(poisson)


def poisson_rate_train_ticket(requests):
    # poisson = 48901 * requests**(-1*1.053)
    rps = [50, 100, 175, 225, 300, 350]
    poisson = [200, 110, 60, 50, 35, 25]
    x = np.array(rps)
    y = np.array(poisson)
    f = interp1d(x, y)
    poisson = f(np.array(requests))
    return int(poisson)


#print(poisson_rate_hr(400))

