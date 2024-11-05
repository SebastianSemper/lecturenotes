import numpy as np
import matplotlib.pyplot as plt

N = 50
l = 3
nIn = np.linspace(0, N - 1, N)
nOut = np.linspace(-l, N - 1, N + 1 * l)
nOut2 = np.linspace(-2 * l, N - 1, N + 2 * l)
nOut3 = np.linspace(-3 * l, N - 1, N + 3 * l)


def MA(x, l):
    xpad = np.pad(x, (l, l))
    y = np.zeros_like(xpad)
    for n in range(x.size + l):
        y[n] = np.mean(xpad[n : n + l])
    return y[:-l]


def MA2(x, l):
    return MA(MA(x, l), l)


delta = np.eye(N)[0, :]
h = MA(delta, l)
h2 = MA2(delta, l)
h3 = MA2(MA(delta, l), l)
h4 = MA(MA2(delta, l), l)

x = np.random.randn(N)
y1 = MA(x, l)
y2 = MA2(x, l)
y3 = MA(MA2(x, l), l)

plt.subplot(211)
plt.stem(
    nIn[: l + 1],
    delta[: l + 1],
    linefmt="r",
    label="delta",
)
plt.stem(
    nOut[: 2 * l + 1] + 0.05,
    h[: 2 * l + 1],
    linefmt="b",
    label="h1",
)
plt.stem(
    nOut2[: 2 * l + 1] + 0.1,
    h2[: 2 * l + 1],
    linefmt="y",
    label="h2",
)
plt.stem(
    nOut3[: 3 * l + 1] + 0.15,
    h3[: 3 * l + 1],
    linefmt="g",
    label="h1 * h2",
)
plt.stem(
    nOut3[: 3 * l + 1] + 0.2,
    h4[: 3 * l + 1],
    linefmt="g",
    label="h2 * h1",
)
plt.legend()
plt.subplot(212)
plt.stem(nIn, x, linefmt="r", label="x")
plt.stem(
    nOut + 0.1, y1, linefmt="b", label="MA(x)"
)
plt.stem(
    nOut2 + 0.2, y2, linefmt="y", label="MA2(x)"
)
plt.stem(
    nOut3 + 0.3,
    y3,
    linefmt="g",
    label="MA2(MA(x))",
)
plt.legend()
plt.show()
