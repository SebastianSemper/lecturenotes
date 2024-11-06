import numpy as np
import matplotlib.pyplot as plt


def complex_exp(
    n: np.ndarray[int], a: complex
) -> np.ndarray[complex]:
    return np.abs(a) ** n * np.exp(
        1j * np.angle(a) * n
    )


n = np.linspace(-2, +10, 13, dtype=int)
a = 0.4 + 1j * 0.6
plt.stem(
    n,
    complex_exp(n, a).real,
    linefmt="r",
    label="real",
)
plt.stem(
    n + 0.1,
    complex_exp(n, a).imag,
    linefmt="b",
    label="imag",
)
plt.legend()
plt.show()
