import numpy as np
import matplotlib.pyplot as plt
from scipy.special import sinc


def gen_receive(x, tau, gamma):
    return np.sum(
        [
            np.roll(x, tt) * gg
            for tt, gg in zip(tau, gamma)
        ],
        axis=0,
    )


N = 64
tau = [14, 34]
gamma = [1, 0.75]

x = np.sin(np.linspace(0, 10 * np.pi, N))
x = np.sinc(np.linspace(-25, +25, N))
# x = np.sign(np.random.randn(N))
X = np.fft.fft(x)

y = gen_receive(x, tau, gamma)
Y = np.fft.fft(y)

# |\Cref{eq:mseq:corr_conv}|
r_xy = np.fft.ifft(Y * X.conj())

if __name__ == "__main__":
    plt.subplot(211)
    plt.stem(x)
    plt.subplot(212)
    plt.plot(np.abs(r_xy), label="r_xy")

    plt.stem(
        tau,
        np.array(gamma) * np.max(np.abs(r_xy)),
        linefmt="r",
        label="true",
    )
    plt.legend()
    plt.show()
