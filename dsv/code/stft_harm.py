import numpy as np
import matplotlib.pyplot as plt

N = 25
F_s = 25

x = np.sin(2 * np.pi * 0.1 * np.arange(N))

freq_x = np.fft.fftshift(
    np.fft.fftfreq(x.size) * F_s
)
X = np.fft.fftshift(np.fft.fft(x))

x_zp = np.pad(x, (0, 10 * N))

freq_x_zp = np.fft.fftshift(
    np.fft.fftfreq(x_zp.size) * F_s
)
X_zp = np.fft.fftshift(np.fft.fft(x_zp))

plt.plot(
    freq_x, np.abs(X), color="b", label="no zp"
)
plt.plot(
    freq_x_zp + 0.1,
    np.abs(X_zp),
    color="r",
    label="zp11",
)
plt.xlabel("F [Hz]")
plt.ylabel("|X[]|")
plt.legend()
plt.show()
