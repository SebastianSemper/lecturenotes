import numpy as np
import matplotlib.pyplot as plt
from matplotlib import colormaps

N = 40
x = np.zeros(N)
k = N // 4
x[:k] += np.ones(k)

res = 128
real = np.linspace(-2, +2, res, endpoint=True)
imag = np.linspace(-2, +2, res, endpoint=True)
zValues = np.concatenate(
    [
        gg.flatten()[None, :]
        for gg in np.meshgrid(
            real,
            imag,
        )
    ]
).T

zTrafo = np.array(
    [
        (
            x
            * (zz[0] + 1j * zz[1])
            ** (-np.arange(N))
        ).sum()
        for zz in zValues
    ]
).reshape(res, res)

dtftValues = np.exp(
    1j
    * 2
    * np.pi
    * np.linspace(0, 1, 201, endpoint=True)
)
dtft = np.array(
    [
        (x * zz ** (-np.arange(N))).sum()
        for zz in dtftValues
    ]
)
dft = np.fft.fft(x)

fig, ax = plt.subplots(
    subplot_kw={"projection": "3d"}
)
ax.plot_surface(
    zValues[:, 0].reshape(res, res),
    zValues[:, 1].reshape(res, res),
    np.minimum(
        np.maximum(np.log(np.abs(zTrafo)), -5),
        5,
    ),
    cmap=colormaps["bone_r"],
    alpha=0.5,
    shade=True,
)
ax.plot(
    dtftValues.real,
    dtftValues.imag,
    np.minimum(
        np.maximum(np.log(np.abs(dtft)), -5),
        5,
    ),
    color="b",
    label="log|dtft(x)|",
    zorder=-3,
)
ax.stem(
    np.cos(2 * np.pi * np.fft.fftfreq(x.size)),
    np.sin(2 * np.pi * np.fft.fftfreq(x.size)),
    np.minimum(
        np.maximum(np.log(np.abs(dft)), -5),
        5,
    ),
    linefmt="r",
    markerfmt="*r",
    label="log|dft(x)|",
)
plt.legend()
plt.show()
