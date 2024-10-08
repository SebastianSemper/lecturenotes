def cubic_spline(t: np.ndarray) -> np.ndarray:
    s1: np.ndarray = 2.0 / 3.0 - np.abs(t) ** 2 + 0.5 * np.abs(t) ** 3
    s2: np.ndarray = (2 - np.abs(t)) ** 3 / 6
    s3: np.ndarray = np.zeros_like(t)
    return s3 + s1 * (np.abs(t) < 1) + s2 * (np.abs(np.abs(t) - 1.5) <= 0.5)
