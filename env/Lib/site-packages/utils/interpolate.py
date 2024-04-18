from utils.util import getDistances, getWeights

def interpolateElevation(point: tuple[float], points: list[tuple[float]], point_values: list[tuple[float]]) -> float:
    """
    Args:
        point (tuple[float]): the point to be looked at in isn93
        w (Window): a window of a dataset containing the elevation of points surrounding a given point
    Returns:
        A single value representing the elevation at given point
    """
    try:
        distances = getDistances(point, points)
        T, d = sum(distances), len(points)
        weights = getWeights(distances, T, d-1)

        assert round(sum(weights),6) == 1, "The weights didn't sum up to 1"

        res = sum([weights[i] * point_values[i] for i in range(d)])

        return res
    except Exception as e:
        print(f"Unable to bridge elevation with exception {e}")