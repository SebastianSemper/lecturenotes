import numpy as np
import matplotlib.pyplot as plt

N = 8

X = np.fft.fft(np.eye(N))
x_DC = X[:, 0]
x_Nyquist = X[:, N // 2]

plt.stem(
    np.arange(N),
    x_DC,
    linefmt="b",
    label="DC-Sequenz",
)
plt.stem(
    np.arange(N) + 0.1,
    x_Nyquist,
    linefmt="r",
    label="Nyquist-Sequenz",
)
plt.legend()
plt.show()
