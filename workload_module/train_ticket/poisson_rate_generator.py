import numpy as np
from scipy.interpolate import interp1d


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

