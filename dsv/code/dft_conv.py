import numpy as np
import matplotlib.pyplot as plt

N = 64
F = 3
T = np.linspace(0, 1, N)
cutOff = 0.05
sin = np.sin(2 * np.pi * 3 * T)
x = sin + 0.1 * np.random.randn(N)
h = np.zeros_like(T) + 1 * (T < cutOff)
h /= np.sum(h)

# zirkulare faltung im zeitbereich
# |\Cref{eq:fourier:cyclic_conv}|
y1 = np.convolve(x, np.tile(h, 2))[N : 2 * N]
y2 = np.fft.ifft(
    np.fft.fft(x) * np.fft.fft(h)
).real

plt.subplot(311)
plt.plot(T, sin, color="blue")
plt.stem(T, x, linefmt="r")

plt.subplot(312)
plt.stem(T, h)

plt.subplot(313)
plt.plot(T, sin, color="blue")
plt.stem(T, y1, linefmt="r")
plt.stem(T + 1 / (5 * N), y2, linefmt="g")

plt.show()
