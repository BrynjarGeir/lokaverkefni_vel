import numpy as np
from rasterio.windows import Window
import rasterio
from math import exp, log, cos, sin, pi
from utils.bridging import bridgeElevation
from utils.util import flattenTo2dPoint

def findLandscapeDistribution(point: tuple[float], d: float = 45, n: int = 20, k: int = 10,
                               angleRange: list[float] = [-15, -10, -5, 0, 5, 10, 15]) -> np.array:
    """
    Args:
        point (tuple[float]): a given point (vedurathugun) that starts the arc
        n (int): the kilometer distance to be looked at (max distance from the vedurathugun)
        k (int): the number of points to be looked at in the along the radius of the arc
        d (float): the direction of the wind
        a (int): the number of angles to divie the arc into
    Returns:
        an array of shape k x len(angles) of points that need to be bridged by Carra data to find the feature values
        at the calculated points
    """
    x, y = point
    angles = [(angle + (90-d)) * pi/180 for angle in angleRange]
    length_rng = [(exp(i * log(n+1)/k) - 1) * 1000 for i in range(1, k+1)]
    points = np.array([[(x + l*cos(angle), y + l*sin(angle)) for angle in angles] for l in length_rng])        
    return points

def findLandscapeElevation(point: tuple[float], index, transform, tifPath: str = "/mnt/d/Skóli/lokaverkefni_vel/data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif") -> float:
    """
    Args:
        point (tuple[float]): a x,y point representing the latitude and longitude of a given point
        index: a function to retrive the index of given coordinates in the dataset
        transform: a function to retrieve coordinates of the given points in dataset
        tifPath (str): a string representing the dictionary where the quadTree indices pkl files are kept
        gridSpacing (float): the spacing of the elevation grid (that is 20m for given tif file)
    Returns:
        A float value that represents the elevation at the given point
    """
    y, x = point
    rStart, cStart = index(x, y)
    rStart, cStart = rStart - 1, cStart - 1
    if rStart < 0:
        width = 2
    else:
        width = 3
    if cStart < 0:
        height = 2
    else:
        height = 3
    rStart, cStart = max(0, rStart), max(0, cStart)
    window = Window(cStart, rStart, height, width)
    with rasterio.open(tifPath) as dataset:
        w = dataset.read(1, window=window)
    coordinates = findLandscapeCoordinates(transform, rStart, cStart)
    elevation = bridgeElevation(point, w, coordinates)
    if elevation <= 3e-38:
        elevation = 0
    return elevation

def findLandscapeElevationPoints(points: list[tuple[float]], tifPath: str = "/mnt/d/Skóli/lokaverkefni_vel/data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif") -> list[float]:
    """
    Args:
        points (list[tuple[float]]): a list of points to estimate the elevation of
        tifPath (str): a string representation of the path to GeoTiff file of elevation of Iceland
    Returns:
        a list of floats representing the elevavtion of points in a distribution
    """
    with rasterio.open(tifPath) as dataset:
        index = dataset.index
        transform = dataset.transform

    points = flattenTo2dPoint(points)
    res = [findLandscapeElevation(point, index, transform) for point in points] 
    return res
        
def findLandscapeCoordinates(transform, r, c) -> tuple[list[float]]:
    """
    Args:
        transform: a transform function, given index, get isn93 coordinates
        r,c: the starting row, col (width, height (3,3))
    Returns:
        a list of elevations and coordinates for all points in the given window
    """
    coordinates = [transform * [c, r], transform * [c, r+1], transform * [c, r+2], transform * [c+1, r], transform * [c+1, r+1],
                transform * [c+1, r+2], transform * [c+2, r], transform * [c+2, r+1], transform * [c+2, r+2]]
    return coordinates