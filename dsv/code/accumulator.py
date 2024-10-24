import numpy as np
import matplotlib.pyplot as plt

n = np.arange(100)
x_1_n = np.cos(2 * np.pi * 0.1 * n)
x_2_n = np.cos(2 * np.pi * 0.05 * n) * np.exp(
    -n / 20
)

y_0 = 1


y_1_n = np.concatenate(
    [[y_0], y_0 + np.cumsum(x_1_n)]
)
y_2_n = np.concatenate(
    [[y_0], y_0 + np.cumsum(x_2_n)]
)

plt.subplot(211)
plt.stem(
    np.arange(100),
    x_1_n,
    label="x1[n]",
    linefmt="b",
)
plt.stem(
    np.arange(100) + 0.1,
    x_2_n,
    label="x2[n]",
    linefmt="r",
)
plt.legend()
plt.subplot(212)
plt.stem(
    np.arange(101),
    y_1_n,
    label="y1[n]",
    linefmt="b",
)
plt.stem(
    np.arange(101) + 0.1,
    y_2_n,
    label="y2[n]",
    linefmt="r",
)
plt.legend()
plt.show()
