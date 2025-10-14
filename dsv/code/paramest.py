import numpy as np
from scipy.optimize import minimize


def log_likelihood(mean, variance, values):
    return (
        np.sum(0.5 * (values - mean) ** 2 / variance)
        + np.log(variance) * values.size * 0.5
    )


def fit_parameters(values):
    def objective(x):
        mean = x[0]
        variance = x[1]
        return log_likelihood(mean, variance, values)

    return minimize(objective, np.array([np.mean(values), np.var(values)]))


x = 2 * np.random.randn(100) + 4
print(fit_parameters(x))

print(np.mean(x), np.var(x))
