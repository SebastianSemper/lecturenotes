import numpy as np
import matplotlib.pyplot as plt


def X(t):
    return np.sin(
        2 * np.pi * t
    ) + 0.3 * np.random.randn(t.size)


N = 1000
T = np.linspace(0, 1, 255, endpoint=False)

X_t = [X(T) for nn in range(N)]

n1, n2 = 10, 190
t1, t2 = T[n1], T[n2]
X_t1 = [X_t[nn][n1] for nn in range(N)]
X_t2 = [X_t[nn][n2] for nn in range(N)]


plt.figure(figsize=[6.4, 6.4], layout="tight")
plt.subplot(211)
[
    plt.plot(T, xx, alpha=0.002, color="black")
    for xx in X_t
]
plt.axvline(t1, color="red")
plt.axvline(t2, color="green")
plt.subplot(212)
plt.hist(X_t1, bins=40, color="red")
plt.hist(X_t2, bins=40, color="green")
plt.savefig("signal2.png")
