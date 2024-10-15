import numpy as np
import matplotlib.pyplot as plt

F_max = 1.0
F = np.random.choice(
    np.linspace(-F_max, +F_max, 11, endpoint=True), 
    2, replace=False
)  # Hz
theta = np.random.uniform(0, 2 * np.pi, 2)  # rad
A = np.random.randn(2)  # amplitude


def x_a(t: np.ndarray) -> np.ndarray:
    return np.sum(np.cos(
        2 * np.pi * np.outer(t, F) + theta) * A, axis=1)


t = np.linspace(0, 5, 1024)

F_s = 3


def g(t: np.ndarray) -> np.ndarray:
    nenner = np.pi * F_s * t
    nenner[np.isclose(t, 0)] = 1
    result = np.sin(np.pi * F_s * t) / nenner
    result[np.isclose(t, 0)] = 1
    return result


n = np.arange(int(t[-1] * F_s)).astype(float) / F_s
x_n = x_a(n)
for nn in np.arange(len(n)):
    plt.plot(t, x_n[nn] * g(t - nn / F_s), 
             color="grey")
plt.scatter(n, x_n, label="x[n]")
plt.plot(t, x_a(t), color="black", 
         linewidth=2, label="x_a")
plt.legend()
plt.show()
