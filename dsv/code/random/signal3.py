import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve


def X(t):
    return np.sin(
        2 * np.pi * 5 * t + np.random.uniform(0, 2 * np.pi, 1)
    ) + 0.3 * np.random.randn(t.size)


N = 1000
T = np.linspace(0, 1, 255, endpoint=False)

X15 = [X(T) for nn in range(5)]

XN = np.array([X(T) for nn in range(N)])

acf = np.mean([fftconvolve(XN[nn, :], XN[nn, ::-1]) for nn in range(N)], axis=0)

plt.figure(figsize=[6.4, 9.6], layout="tight")

plt.subplot(311)
[plt.plot(T, xx) for xx in X15]

plt.subplot(312)
plt.hist(XN[:, 10], density=True, alpha=0.5, label="X_10")
plt.hist(XN[:, 50], density=True, alpha=0.5, label="X_50")
plt.legend()

plt.subplot(313)
plt.plot(acf)

plt.savefig("signal3.png")
