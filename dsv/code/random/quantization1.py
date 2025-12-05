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


F_s = 16  # sampling freq
N_s = 64  # sample duration
T = np.linspace(
    0, N_s / F_s, N_s, endpoint=False
)

# quantisation level both in pos and neg
numLevels = 1
deltaQ = 1.5 / numLevels

X1 = X(T)


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


X1_q, centers, edges = quantize(
    X1, deltaQ, numLevels
)


plt.figure(figsize=[6.4, 4.8], layout="tight")
[
    plt.axhline(cc, color="grey", linestyle=":")
    for cc in centers
]
[plt.axhline(ee, color="grey") for ee in edges]
plt.plot(T, X1, color="blue", label="X_n")
plt.plot(T, X1_q, color="red", label="q(X_n)")
plt.legend()
plt.savefig("quantization1.png")
