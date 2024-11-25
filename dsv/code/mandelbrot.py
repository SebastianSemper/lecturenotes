import numpy as np
import matplotlib.pyplot as plt

Nx = 2**11
Ny = 2**11
# Rx = (-2.25, +1.25)
Rx = (-1.908, -1.906)
# Ry = (-1.75, +1.75)
Ry = (-0.001, +0.001)
c = np.add.outer(
    np.linspace(*Rx, Nx, endpoint=True),
    1j * np.linspace(*Ry, Ny, endpoint=True),
)
z = c.copy()

active = (z.real**2 + z.imag**2) < 4
counter = np.zeros((Nx, Ny))
for ii in range(100):
    z[active] = z[active] ** 2 + c[active]
    counter[active] += 1
    active = (z.real**2 + z.imag**2) < 4

plt.imshow(counter.T**0.3, cmap="bone_r")
plt.show()
