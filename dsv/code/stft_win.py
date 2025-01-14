import numpy as np
import matplotlib.pyplot as plt
from scipy.signal.windows import hann

N = 25
F_s = 25

x = np.sin(
    2 * np.pi * 0.1 * np.arange(N)
) + 0.05 * np.sin(2 * np.pi * 0.2 * np.arange(N))

x_1 = np.pad(x, (0, 10 * N))

freq_x = np.fft.fftshift(
    np.fft.fftfreq(x_1.size) * F_s
)
X_1 = np.fft.fftshift(np.fft.fft(x_1))

x_2 = np.pad(
    x * hann(x.size, sym=False), (0, 10 * N)
)
X_2 = np.fft.fftshift(np.fft.fft(x_2))

plt.semilogy(
    freq_x,
    np.abs(X_1),
    color="r",
    label="rect",
)
plt.semilogy(
    freq_x,
    np.abs(X_2),
    color="b",
    label="hann",
)
[
    plt.axvline(xx)
    for xx in [
        0.1 * F_s,
        0.2 * F_s,
        -0.1 * F_s,
        -0.2 * F_s,
    ]
]
plt.xlabel("F [Hz]")
plt.ylabel("|X[]|")
plt.legend()
plt.show()
