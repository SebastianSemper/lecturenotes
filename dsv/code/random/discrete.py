import numpy as np
import matplotlib.pyplot as plt

D = np.array([-1, 2, 3, 1, 0.1, np.pi])
p = np.array([1, 2, 2, 3, 6, 9])
p = p / np.sum(p)  # so that sum(p) = 1


def pdf(x):
    where = D <= x
    return np.sum(p[where])


x = np.linspace(-2, +4, 1000)

plt.stem(D, p)
plt.plot(x, [pdf(xx) for xx in x], color="r")
plt.xlim(x.min(), x.max())

plt.savefig("discrete.png")
plt.show()
