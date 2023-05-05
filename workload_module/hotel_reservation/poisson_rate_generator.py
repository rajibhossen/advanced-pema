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
    rps = [1200, 1070, 960, 870, 787, 708, 650, 600, 560, 515, 470, 450, 425, 405, 380, 360, 300, 260, 226, 205,
           182, 170, 160, 147, 136, 125, 110, 95, 84, 76, 70, 64, 58, 54, 52, 49, 47, 46, 44, 42]
    poisson = [25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 120, 140, 160, 180, 200, 220, 240,
               260, 280, 300, 350, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 950, 1000]
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

