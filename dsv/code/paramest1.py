import matplotlib.pyplot as plt

import numpy as np

from scipy.stats import expon


def monteCarlo():
    data = expon.rvs(0, 4, 100)

    loc, scale = expon.fit(data)

    return np.std(data), scale


plt.figure()
sizes = [10, 50, 100, 500, 1000, 5000, 10000, 50000]
trials = np.mean(
    [
        (
            np.array(
                [
                    np.mean(np.array([monteCarlo() for ii in range(nn)]), axis=0)
                    for nn in sizes
                ]
            )
            - 4
        )
        ** 2
        for tt in range(50)
    ],
    axis=0,
)
print(trials.shape)
plt.subplot(121)
plt.loglog(sizes, trials[:, 0], label="mean")
plt.loglog(sizes, trials[:, 1], label="ML")
plt.ylabel("bias^2 [log]")
plt.legend()

trials = np.array([monteCarlo() for ii in range(1000)])
plt.subplot(122)
plt.hist(trials[:, 0], bins=20, label="mean")
plt.hist(trials[:, 1], bins=20, label="ML")
plt.axvline(4, color="r", label="true")
plt.axvline(np.mean(trials[:, 0]), color="b", label="mean")
plt.axvline(np.mean(trials[:, 1]), color="g", label="ML")
plt.legend()
plt.savefig("paramest1.png")
