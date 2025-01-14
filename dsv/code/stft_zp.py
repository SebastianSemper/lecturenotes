import numpy as np
import matplotlib.pyplot as plt

N = 25
F_s = 25

x = np.zeros(N)
x[: N // 5] = 1

freq_x = np.fft.fftshift(
    np.fft.fftfreq(x.size) * F_s
)
X = np.fft.fftshift(np.fft.fft(x))

x_zp = np.pad(x, (0, 2 * N))

freq_x_zp = np.fft.fftshift(
    np.fft.fftfreq(x_zp.size) * F_s
)
X_zp = np.fft.fftshift(np.fft.fft(x_zp))

plt.stem(freq_x, np.abs(X), linefmt="b")
plt.stem(
    freq_x_zp + 0.1, np.abs(X_zp), linefmt="r"
)
plt.show()
