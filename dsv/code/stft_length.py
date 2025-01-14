import numpy as np
import matplotlib.pyplot as plt


def f(t):
    if t < 5:
        return np.cos(2 * np.pi * t * 10)
    elif t < 10:
        return np.cos(2 * np.pi * t * 25)
    elif t < 15:
        return np.cos(2 * np.pi * t * 50)
    else:
        return np.cos(2 * np.pi * t * 100)


F_s = 400.0  # Hz
T_max = 20.0  # s
T = np.linspace(0, T_max, int(T_max * F_s))  # s

W = 2.0  # s
W_N = int(F_s * W)  # samples

x = np.array([f(tt) for tt in T])
X = x.reshape((-1, W_N)).T

F = np.fft.fftshift(np.fft.fftfreq(1024)) * F_s

STFT = np.fft.fftshift(
    np.fft.fft(X, n=1024, axis=0), axes=0
)

plt.imshow(
    np.abs(STFT),
    extent=[T[0], T[-1], F[0], F[-1]],
    cmap="bone",
)
ax = plt.gca()
ax.set_xlim(T[0], T[-1])
ax.set_ylim(F[-1], F[0])
plt.ylabel("F [Hz]")
plt.xlabel("t [s]")
plt.colorbar()
plt.gca().set_aspect("auto")
plt.show()
