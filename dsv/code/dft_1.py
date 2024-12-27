import numpy as np
import matplotlib.pyplot as plt


def x_k(k: int, N: int) -> np.ndarray[complex]:
    return np.exp(
        1j * 2 * np.pi * k * np.arange(N) / N
    )


N = 40
x = np.zeros(N)
k = N // 4
x[:k] += np.ones(k)

c1 = np.array(
    [
        (x * x_k(kk, N).conj()).sum() / N
        for kk in range(N)
    ]
)
F = np.array([x_k(kk, N) for kk in range(N)]).T
c2 = F.conj().T.dot(x) / N

plt.subplot(211)
plt.stem(x)

plt.subplot(212)
plt.stem(
    np.arange(N),
    np.abs(c1),
    linefmt="r",
    label="Abs(c1)",
)
plt.stem(
    np.arange(N) + 0.2,
    np.abs(c2),
    linefmt="b",
    label="Abs(c2)",
)
plt.legend()
plt.show()
