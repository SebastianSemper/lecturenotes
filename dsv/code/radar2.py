import numpy as np
import matplotlib.pyplot as plt
from mlbs import gen_MLBS
from radar1 import gen_receive

x = gen_MLBS(0x44, 1)

tau = [14, 34]
gamma = [1, 0.3]

N = x.size

x = x
X = np.fft.fft(x)

y = gen_receive(x, tau, gamma) + (
    0.5 * np.random.randn(x.size)
)
Y = np.fft.fft(y)

r_xy = np.fft.ifft(Y * X.conj())

plt.subplot(311)
plt.title("y")
plt.stem(y)
plt.subplot(312)
plt.title("DFT(x)")
plt.stem(np.abs(X))
plt.subplot(313)
plt.title("r_{x,y}")
plt.plot(np.abs(r_xy), label="r_xy")
plt.stem(
    tau,
    np.array(gamma) * np.max(np.abs(r_xy)),
    linefmt="r",
    label="true",
)
plt.legend()
plt.show()
