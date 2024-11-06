import numpy as np
import matplotlib.pyplot as plt


# assume n=0 in center, size(x_n) = 2K+1
def even(x_n: np.ndarray) -> np.ndarray:
    return 0.5 * (x_n + x_n[::-1])


# assume n=0 in center, size(x_n) = 2K+1
def odd(x_n: np.ndarray) -> np.ndarray:
    return 0.5 * (x_n - x_n[::-1])


K = 7
n = np.linspace(-K, +K, 2 * K + 1)
x_n = np.random.randn(n.size)

plt.stem(n, x_n, linefmt="g", label="x_n")
plt.stem(
    n + 0.05, even(x_n), linefmt="r", label="x_g"
)
plt.stem(
    n - 0.05, odd(x_n), linefmt="b", label="x_u"
)
plt.stem(
    n - 0.1,
    even(x_n) + odd(x_n),
    linefmt="y",
    label="x_g + x_u",
)
plt.legend()
plt.axvline(0)
plt.show()
