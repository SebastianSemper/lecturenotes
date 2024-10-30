import numpy as np
import matplotlib.pyplot as plt

theta = -np.pi / 2  # rad
F = 1.5  # Hz
F_s = 1.8  # Hz
T_s = 1.0 / F_s  # s

F_alias1 = F - 1 * F_s  # Hz
F_alias2 = F + 1 * F_s  # Hz


def x_a(t, F, theta):
    return np.cos(2 * np.pi * F * t + theta)


T = np.linspace(0, 3, 301, endpoint=True)  # s
n = np.arange(4) * T_s  # none

plt.plot(T, x_a(T, F, theta), label="x_a")
plt.plot(
    T, x_a(T, F_alias1, theta), label="x_alias1"
)
plt.plot(
    T, x_a(T, F_alias2, theta), label="x_alias2"
)
plt.scatter(
    n, x_a(n, F, theta), color="r", label="x[n]"
)
plt.legend()
plt.show()
