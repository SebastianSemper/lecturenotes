import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ecdf
from scipy.special import sinc


def X(t):
    return (
        0.2
        * np.sin(
            2 * np.pi * 0.75 * t
            + np.random.uniform(0, 2 * np.pi, 1)
        )
        + np.sin(
            2 * np.pi * 1.5 * t
            + np.random.uniform(0, 2 * np.pi, 1)
        )
        + 0.3 * np.random.randn(t.size)
    )


N = 100
F_s = 16  # sampling freq
N_s = 64  # sample duration
T = np.linspace(
    0, N_s / F_s, N_s, endpoint=False
)
# quantisation level both in pos and neg
numLevels = 7
deltaQ = 2.5 / numLevels

XN = np.array([X(T) for nn in range(N)])


def quantize(x, deltaQ, levels):
    q = np.round(x / deltaQ) * deltaQ
    q[q < (-levels - 0.5) * deltaQ] = (
        -levels * deltaQ
    )
    q[q > (levels + 0.5) * deltaQ] = (
        levels * deltaQ
    )
    centers = np.linspace(
        -levels * deltaQ,
        +levels * deltaQ,
        2 * levels + 1,
        endpoint=True,
    )
    edges = np.concatenate(
        [
            centers - deltaQ / 2,
            [centers[-1] + deltaQ / 2],
        ]
    )
    return q, centers, edges


def empirical_pdf(x, edges):
    density_eval = np.linspace(
        edges[0],
        edges[-1],
        int(10 * (edges[-1] - edges[0])),
    )
    # |\Cref{eq:random:cdf}|
    x_ecdf = ecdf(XN.flatten()).cdf

    # |\Cref{eq:random:pdf_approx}|
    x_ecfd_vals = x_ecdf.evaluate(density_eval)

    # numerical differentiation
    x_epdf = (
        0.5
        * (x_ecfd_vals[2:] - x_ecfd_vals[:-2])
        / np.diff(density_eval)[0]
    )

    return x_epdf, density_eval[1:]


def invert_quant(X_f_q, evalGrid, centers):
    # stuetzstellen im freq-bereich
    f_bins = np.fft.fftfreq(X_f_q.size)

    # schaetzung von phi_X
    X_phi_q = np.fft.fft(X_f_q)

    # diskreter integrator
    X_phi = X_phi_q / np.where(
        np.isclose(
            1 - np.exp(1j * 2 * np.pi * f_bins),
            0,
        ),
        1,
        1 - np.exp(1j * 2 * np.pi * f_bins),
    )

    # differenzieren
    X_phi = X_phi * (-1j * 2 * np.pi * f_bins)

    # shift
    X_phi = X_phi * np.exp(
        1j * 2 * np.pi * f_bins / 2
    )

    # transformation in Zeitbereich
    X_f = np.fft.ifft(X_phi).real
    X_f = X_f - X_f[0]

    # sinc-interpolation
    shift = np.diff(centers)[0]
    X_f_fine = sinc(
        np.add.outer(evalGrid, -centers) / shift
    ).dot(X_f)

    return X_f, X_f_fine


XN_q, centers, edges = quantize(
    XN, deltaQ, numLevels
)
XN_f, density_eval = empirical_pdf(
    XN.flatten(), edges
)
XN_f_q, _ = np.histogram(
    XN_q, edges, density=True
)

XN_f_est, XN_phi_est = invert_quant(
    XN_f_q, density_eval, centers
)

plt.figure(layout="tight")

plt.plot(
    density_eval[:-1],
    XN_f,
    color="b",
    label="$f_X$",
)
plt.stem(
    centers,
    XN_f_q,
    markerfmt="r",
    basefmt="r",
    linefmt="r",
    label="$f_{q(X)}$",
)
plt.plot(
    density_eval,
    XN_phi_est,
    color="g",
    label="estimate of $f_X$",
)
[
    plt.axvline(ee, color="grey", linestyle=":")
    for ee in edges
]
plt.legend()

plt.savefig("quantization3.png")
