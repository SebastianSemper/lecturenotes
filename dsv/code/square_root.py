import numpy as np
import matplotlib.pyplot as plt


def root(A: float, y0: float, n):
    y = [y0]
    for ii in range(n):
        y.append((y[-1] + A / y[-1]) / 2)

    return y


A = 5.0
rootA = np.sqrt(A)
y = root(A, 1.0, 6)

plt.subplot(211)
plt.stem(y)
plt.ylabel("y[n]")
plt.xlabel("Iteration n")
plt.axhline(rootA, linestyle="--", color=)
plt.subplot(212)
plt.semilogy(
    np.abs(np.array(y) - rootA)
)
plt.ylabel("log(|y[n] - sqrt(A)|)")
plt.xlabel("Iteration n")
plt.show()
