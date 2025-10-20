import numpy as np
from scipy.optimize import minimize
from scipy.stats import crystalball, norm
import matplotlib.pyplot as plt


def log_likelihood(mean, variance, values):
    return (
        np.sum((values - mean) ** 2 / variance)
        + np.log(2 * np.pi * variance) * values.size
    )


def log_likelihood_jacobian(mean, variance, values):
    return np.array(
        [
            -np.sum(values - mean) / variance,
            values.size / variance - np.sum((values - mean) ** 2) / variance**2,
        ]
    )


def fit_parameters(values):
    def objective(x):
        mean = x[0]
        variance = x[1]
        return log_likelihood(mean, variance, values)

    def jacobian(x):
        mean = x[0]
        variance = x[1]
        return log_likelihood_jacobian(mean, variance, values)

    return minimize(
        objective, np.array([np.mean(values), np.var(values)]), jac=jacobian
    ).x


num_samples = 10000
x = crystalball.rvs(beta=2.0, m=2.3, loc=3, scale=2, size=num_samples)

mean_hat, var_hat = fit_parameters(x)
beta_hathat, m_hathat, mean_hathat, var_hathat = crystalball.fit(x)

print(mean_hat, var_hat)

plt_x = np.linspace(np.min(x), np.max(x), 50)

plt.figure()
plt.hist(x, bins=20, density=True, log=True, label="data")
plt.semilogy(
    plt_x, norm.pdf(plt_x, loc=mean_hat, scale=np.sqrt(var_hat)), label="normal"
)
plt.semilogy(
    plt_x,
    crystalball.pdf(
        plt_x, beta=beta_hathat, m=m_hathat, loc=mean_hathat, scale=var_hathat
    ),
    label="crystal ball",
)
plt.ylim(1e-6, 1)
plt.legend()
plt.savefig("paramest2.png")
