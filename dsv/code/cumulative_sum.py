import numpy as np
import matplotlib.pyplot as plt


def cumulative_sum(
    x: np.ndarray, n: np.ndarray
) -> np.ndarray:
    y = np.zeros(n.size)
    for nn in n:
        y[nn] = np.sum(x[:nn]) / (nn + 1)

    return y


def cumulative_sum_rec(
    y: float, x: float, n: int
):
    return (n / (n + 1.0)) * y + 1.0 / (
        n + 1
    ) * x


n = np.arange(20)
f = 1.0 / np.exp(1)
x = np.cos(2 * np.pi * f * n)

y1 = cumulative_sum(x, n)
y2 = [0]
for nn in n[1:]:
    y2.append(
        cumulative_sum_rec(
            y2[nn - 1], x[nn - 1], nn
        )
    )
plt.stem(n, x, linefmt="r", label="x[n]")
plt.stem(n + 0.1, y1, linefmt="b", label="y[n]")
plt.stem(
    n + 0.2, y2, linefmt="g", label="y_rec[n]"
)
plt.legend()
plt.show()
