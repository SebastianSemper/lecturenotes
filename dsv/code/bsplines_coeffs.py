import numpy as np


def filter_coeffs(x_n: np.ndarray) -> np.ndarray:
    z_1: float = np.sqrt(3) - 2.0
    c_k_p: np.ndarray = np.zeros_like(x_n)
    c_k_m: np.ndarray = np.zeros_like(x_n)

    c_k_p[0] = np.sum(
        x_n * np.power(z_1, np.arange(x_n.size))
    )

    for kk in range(1, x_n.size):
        c_k_p[kk] = x_n[kk] + z_1 * c_k_p[kk - 1]

    c_k_m[-1] = (
        z_1
        * (c_k_p[-1] + z_1 * c_k_p[-2])
        / (1.0 - z_1**2)
    )

    for kk in range(2, x_n.size + 1):
        c_k_m[-kk] = z_1 * (
            c_k_m[-kk + 1] + c_k_p[-kk]
        )

    return -6 * c_k_m
