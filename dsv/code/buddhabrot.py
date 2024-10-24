import numpy as np
import matplotlib.pyplot as plt


def sample(
    x_0: complex, low: int, hgh: int
) -> tuple[bool, int]:
    x_n: int = x_0
    counter: int = 0
    while (
        x_n.real**2 + x_n.imag**2
    ) < 4 and counter < hgh:
        x_n = x_n**2 + x_0
        counter += 1

    return (
        (low <= counter) and (counter <= hgh),
        counter,
    )


def trial():
    while True:
        yield np.random.uniform(
            -2, +2
        ) + 1j * np.random.uniform(-2, +2)


success = []
for tt in trial():
    valid, counter = sample(tt, 100, 50000)
    if valid:
        success += [(tt, counter)]
    if len(success) > 400:
        break

image = np.zeros((1024, 1024), dtype=int)
for ss in success:
    x_n = ss[0]
    for ii in range(ss[1]):
        image[
            int(
                image.shape[0]
                * (x_n.real / 2 + 0.5)
            )
            % image.shape[0],
            int(
                image.shape[1]
                * (x_n.imag / 2 + 0.5)
            )
            % image.shape[1],
        ] += 1
        x_n = x_n**2 + ss[0]

plt.imshow(image ** (0.01), cmap="bone")
plt.show()
