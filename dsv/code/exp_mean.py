import numpy as np
import matplotlib.pyplot as plt


def exp_mean(
    x: np.ndarray, alpha: float
) -> np.ndarray:
    y = np.zeros_like(x)
    y[0] = 0
    for ii in range(1, y.size):
        y[ii] = (
            alpha * y[ii - 1]
            + (1 - alpha) * x[ii]
        )

    return y


alpha1 = 0.5
alpha2 = 0.1
N = 20
L = 3
n = np.arange(N)
l = np.arange(L)
delta = np.eye(L)[0]
h1 = exp_mean(
    np.pad(delta, (L, L), mode="constant"),
    alpha1,
)[L:-L]
h2 = exp_mean(
    np.pad(delta, (L, L), mode="constant"),
    alpha2,
)[L:-L]

x = np.random.randn(N)
y1 = exp_mean(
    np.pad(x, (L, L), mode="constant"), alpha1
)[L:-L]
y2 = exp_mean(
    np.pad(x, (L, L), mode="constant"), alpha2
)[L:-L]
xh1 = np.convolve(
    np.pad(x, (L, L), mode="constant"),
    h1,
)[L : -(L - 1) - L]
xh2 = np.convolve(
    np.pad(x, (L, L), mode="constant"),
    h2,
)[L : -(L - 1) - L]

plt.subplot(211)
plt.stem(
    l, h1, linefmt="r", label=f"h({alpha1})"
)
plt.stem(
    l + 0.1,
    h2,
    linefmt="b",
    label=f"h({alpha2})",
)
plt.legend()

plt.subplot(212)
plt.stem(
    n, y1, linefmt="g", label=f"y({alpha1})"
)
plt.stem(
    n + 0.2,
    y2,
    linefmt="y",
    label=f"y({alpha2})",
)
plt.stem(
    n + 0.1,
    xh1,
    linefmt="r",
    label=f"x * h({alpha1})",
)
plt.stem(
    n + 0.3,
    xh2,
    linefmt="b",
    label=f"x * h({alpha2})",
)
plt.legend()
plt.show()
