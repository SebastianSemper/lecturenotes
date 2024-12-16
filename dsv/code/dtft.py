import numpy as np
import matplotlib.pyplot as plt


def dtft(
    x: np.ndarray[complex],
    n: np.ndarray[int],
    F: np.ndarray[float],
) -> np.ndarray[complex]:
    return np.array(
        [
            (
                x * np.exp(-2j * np.pi * n * f)
            ).sum()
            for f in F
        ]
    )


def idtft(
    X: np.ndarray[complex],
    F: np.ndarray[float],
    n: np.ndarray[int],
):
    return np.array(
        [
            (F[1] - F[0])
            * (
                X * np.exp(2j * np.pi * nn * F)
            ).sum()
            for nn in n
        ]
    )


N = 20
n = np.linspace(-N, +N, 2 * N + 1)
omega = 1 / np.pi

x = np.sin(omega * n) / (np.pi * n)
x[N] = omega / np.pi
F = np.linspace(-0.5, +0.5, 201)
X_approx = dtft(x, n, F)
X_true = np.zeros_like(F)
X_true[np.abs(F) <= omega / (2 * np.pi)] += 1

x_approx = idtft(X_approx, F, n)
x_true = idtft(X_true, F, n)

plt.subplot(311)
plt.stem(n, x, label="x[n]")
plt.xlabel("n")
plt.legend()

plt.subplot(312)
plt.plot(F, X_approx, label="X_approx(f)")
plt.plot(F, X_true, label="X_true(f)")
plt.xlabel("f")
plt.legend()

plt.subplot(313)
plt.stem(n, x, linefmt="r", label="x[n]")
plt.stem(
    n + 0.1,
    x_approx,
    linefmt="g",
    label="x_approx[n]",
)
plt.stem(
    n + 0.2,
    x_true,
    linefmt="b",
    label="x_true[n]",
)
plt.xlabel("n")
plt.legend()
plt.show()
