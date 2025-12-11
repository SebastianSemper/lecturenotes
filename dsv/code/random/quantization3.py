import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ecdf
from scipy.special import sinc
from scipy.differentiate import derivative


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


N = 10000
F_s = 16  # sampling freq
N_s = 64  # sample duration
T = np.linspace(
    0, N_s / F_s, N_s, endpoint=False
)
# quantisation level both in pos and neg
numLevels = 7
deltaQ = 3.0 / numLevels

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
        int(20 * (edges[-1] - edges[0])),
    )
    # |\Cref{eq:random:cdf}|
    x_ecdf = ecdf(x.flatten()).cdf

    # |\Cref{eq:random:pdf_approx}|
    x_ecfd_vals = x_ecdf.evaluate(density_eval)

    # numerical differentiation
    x_epdf = (
        0.5
        * (x_ecfd_vals[2:] - x_ecfd_vals[:-2])
        / np.diff(density_eval)[0]
    )

    return x_epdf, density_eval[1:]


def lin_extrplt(x, n: tuple[int]):
    diff = np.diff(x)[[0, -1]]
    return np.concatenate(
        [
            x[0]
            - np.arange(1, n[0] + 1)[::-1]
            * diff[0],
            x,
            x[-1]
            + np.arange(1, n[1] + 1) * diff[1],
        ]
    )


def sinc_deriv(x):
    return np.where(
        np.isclose(x, 0),
        np.zeros_like(x),
        ((np.cos(np.pi * x) - sinc(x)) / x),
    )


def invert_quant(X_f_q, evalGrid, centers):
    sinc_shift = np.diff(centers)[0]
    X_f_q_sum = np.cumsum(X_f_q)

    # periodifizierung vermeided ringing
    padded_centers = lin_extrplt(
        centers, (0, X_f_q_sum.size)
    )
    X_f_q_sum = np.concatenate(
        [X_f_q_sum, X_f_q_sum[::-1]]
    )

    return sinc_deriv(
        np.add.outer(
            evalGrid,
            -padded_centers - sinc_shift / 2,
        )
        / sinc_shift
    ).dot(X_f_q_sum)


XN_q, centers, edges = quantize(
    XN, deltaQ, numLevels
)
XN_f, density_eval = empirical_pdf(
    XN.flatten(), edges
)
XN_f_q, _ = np.histogram(
    XN_q, edges, density=True
)

XN_f_ipol = invert_quant(
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
    XN_f_ipol,
    color="g",
    label="estimate of $f_X$",
)
[
    plt.axvline(ee, color="grey", linestyle=":")
    for ee in edges
]
plt.legend()

plt.savefig("quantization3.png")
