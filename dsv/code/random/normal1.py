import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

x = np.linspace(-2, +4, 500)

plt.figure()
plt.plot(x, norm.pdf(x))
plt.plot(x, norm.pdf(x, loc=2, scale=0.4))
plt.plot(x, norm.pdf((x-2)/(0.4))/(0.4), linestyle="-.")

plt.savefig("normal1.png")