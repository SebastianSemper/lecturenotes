import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import ecdf


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
numLevels = 2
deltaQ = 1.5 / numLevels

X15 = np.array([X(T) for nn in range(3)])
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
        edges[0], edges[-1]
    )
    # |\Cref{eq:random:cdf}|
    x_ecdf = ecdf(XN.flatten()).cdf

    # |\Cref{eq:random:pdf_approx}|
    x_epdf = (
        np.diff(x_ecdf.evaluate(density_eval))
        / np.diff(density_eval)[0]
    )

    return x_epdf, density_eval


# |\Cref{eq:random:area_sampling}|
def density_area_sampling(t, x, deltaQ):
    x_ecdf = ecdf(x.flatten()).cdf

    # |\Cref{eq:random:conv_cdf}|
    return (
        x_ecdf.evaluate(t + deltaQ / 2)
        - x_ecdf.evaluate(t - deltaQ / 2)
    ) / deltaQ


X15_q, centers, edges = quantize(
    X15, deltaQ, numLevels
)
XN_f, density_eval = empirical_pdf(
    XN.flatten(), edges
)
XN_q, _, _ = quantize(XN, deltaQ, numLevels)
XN_f_q, _ = np.histogram(
    XN_q, edges, density=True
)
XN_f_q_as = [
    density_area_sampling(
        cc, XN.flatten(), deltaQ
    )
    for cc in centers
]


plt.figure(figsize=[6.4, 6.4], layout="tight")
plt.subplot(211)
[
    plt.axhline(cc, color="grey", linestyle=":")
    for cc in centers
]
[plt.axhline(ee, color="grey") for ee in edges]

[plt.plot(T, xx, color="blue") for xx in X15]
[plt.plot(T, xx, color="red") for xx in X15_q]

plt.subplot(212)
plt.plot(
    density_eval[:-1],
    XN_f,
    color="b",
    label="$f_X$",
)
plt.stem(
    centers - deltaQ / 50,
    XN_f_q,
    markerfmt="r",
    basefmt="r",
    linefmt="r",
    label="$f_{q(X)}$",
)
plt.stem(
    centers + deltaQ / 50,
    XN_f_q_as,
    markerfmt="g",
    basefmt="g",
    linefmt="g",
    label="$(rect_{\\Delta Q} * f_X) \\cdot c$",
)
[
    plt.axvline(ee, color="grey", linestyle=":")
    for ee in edges
]
plt.legend()
plt.savefig("quantization2.png")
