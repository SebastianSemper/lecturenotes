import numpy as np
import matplotlib.pyplot as plt

A = 1.5
F = 2
theta = np.pi / 2


def harm(t: float) -> float:
    return A * np.cos(
        2 * np.pi * (F * t + theta))


def phasor(t: float) -> complex:
    return 0.5 * A * np.exp(
        -1j * (2 * np.pi * (F * t + theta)))


T = np.linspace(0, 1, 255)
plt.plot(T, harm(T), label="harm(T)")
plt.plot(T, phasor(T) + phasor(T).conj(), 
         linestyle="--", label="harm(T)")
plt.xlabel("t")
plt.show()
