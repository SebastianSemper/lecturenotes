import numpy as np
import matplotlib.pyplot as plt

N = 10
l = 4
nIn = np.linspace(0, N - 1, N)
nOut = np.linspace(-l, N - 1 + l, N + 2 * l)


def MA(x, l):
    xpad = np.pad(x, (l, l))
    y = np.zeros_like(xpad)
    for n in range(x.size + l):
        y[n] = np.mean(xpad[n : n + l])
    return y


delta = np.eye(N)[0, :]
h = MA(delta, l)
x = np.random.randn(N)
y1 = MA(x, l)
y2 = np.convolve(x, h[: 2 * l + 1])

plt.subplot(211)
plt.stem(nIn, delta, linefmt="r", label="delta")
plt.stem(nOut + 0.1, h, linefmt="b", label="h")
plt.legend()
plt.subplot(212)
plt.stem(nIn, x, linefmt="r", label="x")
plt.stem(
    nOut + 0.1, y1, linefmt="b", label="MA(x)"
)
plt.stem(
    nOut + 0.2, y2, linefmt="g", label="x * h"
)
plt.legend()
plt.show()
