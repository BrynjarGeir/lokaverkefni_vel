import numpy as np


def interpolateElevation(point: tuple[float], points: list[tuple[float]], point_values: list[tuple[float]]) -> float:
    """
    Args:
        point (tuple[float]): the point to be looked at in isn93
        w (Window): a window of a dataset containing the elevation of points surrounding a given point
    Returns:
        A single value representing the elevation at given point
    """
    try:
        distances = np.linalg.norm(np.array(points) - np.array(point), axis = 1)
        T, d = sum(distances), len(points)
        weights = (T - distances) / ((d-1) * T)

        return np.sum(weights * point_values)

    except Exception as e:
        print(f"Unable to bridge elevation with exception {e}")