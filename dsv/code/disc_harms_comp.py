import numpy as np
import matplotlib.pyplot as plt

A = 1
# f = 1/16
f = 1 / (5 * np.exp(1))
theta = np.pi / 2
# N = 32
N = 72


def harm(n: np.ndarray[int]) -> np.ndarray[complex]:
    return A * np.exp(
        1j * 2 * np.pi * (f * n + theta))


n = np.arange(N)
x_n = harm(n)
fig, ax = plt.subplots(
    subplot_kw={"projection": "polar"})
ax.plot(np.angle(x_n), np.abs(x_n), 
        marker="o", linewidth=0)
print(np.abs(x_n))
plt.show()
