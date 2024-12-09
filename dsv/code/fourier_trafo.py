import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad


def rect(t: float) -> float:
    if np.abs(t) < 0.75:
        return 1
    else:
        return 0


def kernel(t: float, F: float) -> complex:
    return np.exp(1j * 2 * np.pi * F * t)


def analyse(x, Trange: list[float]):
    def x_ft(F: float):
        return quad(
            lambda t: kernel(-t, F) * x(t),
            np.min(Trange),
            np.max(Trange),
            complex_func=True,
        )[0].real

    return x_ft


def synthese(X, Frange: list[float]):
    def x(t: float):
        return quad(
            lambda F: kernel(t, F) * X(F),
            np.min(Frange),
            np.max(Frange),
            complex_func=True,
        )[0].real

    return x


Trange = np.linspace(-3, +3, 121, endpoint=True)
Frange = np.linspace(-6, +6, 121, endpoint=True)

rect_ft = analyse(rect, Trange)
rect_synth = synthese(rect_ft, Frange)


plt.figure()
plt.subplot(211)
plt.plot(
    Trange,
    [rect(tt) for tt in Trange],
)
plt.plot(
    Trange,
    [rect_synth(tt) for tt in Trange],
)
plt.legend()

plt.subplot(212)

plt.plot(
    Frange,
    [rect_ft(ff) for ff in Frange],
)
plt.legend()
plt.show()
