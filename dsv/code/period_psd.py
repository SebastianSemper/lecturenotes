import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

T_0 = 2
F_0 = 1.0 / T_0
Kmax = 30


def x(t: float) -> float:
    if (t < 0.0) or (t > 0.1):
        return 0
    else:
        return 1


def x_k(t: float, k: int) -> complex:
    return np.exp(1j * 2 * np.pi * F_0 * k * t)


def synth(
    t: float, c_k: list[complex], allK: list[int]
) -> complex:
    return np.sum(
        cckk * x_k(t, kk)
        for kk, cckk in zip(allK, c_k)
    )


allK = np.linspace(
    -Kmax, +Kmax, 2 * Kmax + 1, dtype=int
)
c_k = np.array(
    [
        quad(
            lambda t: x_k(t, kk).conj() * x(t),
            0,
            T_0,
            complex_func=True,
        )[0]
        for kk in allK
    ]
)

plt.figure()
plt.stem(
    allK * F_0, np.abs(c_k) ** 2, linefmt="b"
)
plt.ylabel("|c_k|^2")
plt.xlabel("Frequenz")
plt.show()
