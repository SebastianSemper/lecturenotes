import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

T_0 = 1.0
F_0 = 1.0 / T_0
Kmax = 30


def rect(t: float) -> float:
    if (t < 0.0) or (t > 0.3):
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
            lambda t: x_k(t, kk).conj()
            * rect(t),
            0,
            T_0,
            complex_func=True,
        )[0]
        for kk in allK
    ]
)

plt.figure()
plt.subplot(121)
plt.stem(
    allK, c_k.real, linefmt="b", label="Re(c_k)"
)
plt.stem(
    allK + 0.1,
    c_k.imag,
    linefmt="r",
    label="Im(c_k)",
)
plt.legend()

allT = np.linspace(0, T_0, 201, endpoint=False)
plt.subplot(122)
plt.plot(
    allT, [rect(tt) for tt in allT], label="x"
)
plt.plot(
    allT,
    [synth(tt, c_k, allK) for tt in allT],
    label="sum c_k x_k",
)
plt.legend()
plt.show()
