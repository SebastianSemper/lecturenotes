import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve


def X(t):
    return (
        0.2
        * np.sin(
            2 * np.pi * 0.75 * t
            + np.random.uniform(0, 2 * np.pi, 1)
        )
        + np.sin(
            2 * np.pi * 3 * t
            + np.random.uniform(0, 2 * np.pi, 1)
        )
        + 0.6 * np.random.randn(t.size)
    )


N = 1000
F_s = 16  # sampling freq
N_s = 64  # sample duration
T = np.linspace(
    0, N_s / F_s, N_s, endpoint=False
)

X15 = [X(T) for nn in range(5)]

XN = np.array([X(T) for nn in range(N)])

acf = np.mean(
    [
        fftconvolve(XN[nn, :], XN[nn, ::-1])
        for nn in range(N)
    ],
    axis=0,
)
psd = np.fft.fft(acf, n=5 * acf.size)

plt.figure(figsize=[6.4, 9.6], layout="tight")

plt.subplot(411)
[plt.plot(T, xx) for xx in X15]

plt.subplot(412)
plt.hist(
    XN[:, 10],
    density=True,
    alpha=0.5,
    label="X_10",
)
plt.hist(
    XN[:, 50],
    density=True,
    alpha=0.5,
    label="X_50",
)
plt.legend()

plt.subplot(413)
plt.plot(acf, label="gamma_{X,X}")
plt.legend()

plt.subplot(414)
plt.semilogy(
    np.fft.fftshift(np.fft.fftfreq(psd.size))
    * F_s,
    np.fft.fftshift(np.abs(psd)),
    label="S(F)",
)
plt.axvline(-3, color="red")
plt.axvline(+3, color="red")
plt.axvline(-0.75, color="red")
plt.axvline(+0.75, color="red")
plt.legend()

plt.savefig("signal3.png")
