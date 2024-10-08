import numpy as np
import matplotlib.pyplot as plt

A = 1.5
f = 0.1
theta = np.pi / 2

def harm(n: int) -> float:
    return A * np.cos(
        2 * np.pi * f * n + theta)

n = np.arange(16)
plt.stem(n, harm(n), label="harm[n]")
plt.xlabel("n")
plt.show()
