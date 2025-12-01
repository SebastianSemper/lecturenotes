import numpy as np
import matplotlib.pyplot as plt


def X(t):
    return np.sin(
        2 * np.pi * t
    ) + 0.3 * np.random.randn(t.size)


T = np.linspace(0, 1, 127, endpoint=False)
plt.figure()
plt.plot(T, X(T))
plt.plot(T, X(T))
plt.plot(T, X(T))
plt.savefig("signal1.png")
