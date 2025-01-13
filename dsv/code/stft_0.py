import numpy as np
import matplotlib.pyplot as plt


def f(t):
    if t < 5:
        return np.cos(2 * np.pi * t * 10)
    if t < 10:
        return np.cos(2 * np.pi * t * 25)
    if t < 15:
        return np.cos(2 * np.pi * t * 50)
    return np.cos(2 * np.pi * t * 100)


F_s = 400  # Hz
T_max = 20  # s
T = np.linspace(0, T_max, T_max * F_s)  # s

W = 0.25  # s
W_N = int(F_s * W)  # samples

F = np.fft.fftshift(np.fft.fftfreq(W_N)) * F_s

x = np.array([f(tt) for tt in T])

X = x.reshape((-1, W_N)).T


plt.imshow(
    np.abs(
        np.fft.fftshift(np.fft.fft(X, axis=0))
    ),
    extent=[T[0], T[-1], F[0], F[-1]],
)
ax = plt.gca()
ax.set_xlim(T[0], T[-1])
ax.set_ylim(F[-1], F[0])

plt.show()
