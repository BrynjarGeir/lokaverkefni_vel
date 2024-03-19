import numpy as np
from math import exp, log, cos, sin, pi
from utils.bridging import bridgeElevation
from utils.util import flattenTo2dPoint
from utils.getPickledObjects import calcIndex, calcTransform
import numpy as np
import math

def getOtherPointsOffset(given_point: tuple[float], closest_point: tuple[float]) -> list[tuple[int]]:
    x, y = given_point
    xi, yi = closest_point
    if x < xi and y < yi:
        return [(0, 1), (1, 0), (1, 1)]
    elif x < xi and y >= yi:
        return [(-1, 0), (-1, 1), (0, 1)]
    elif x >= xi and y >= yi:
        return [(-1, -1), (-1, 0), (0, -1)]
    else:
        return [(0, -1), (1, -1), (1, 0)]

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
    assert not np.any(np.isnan(points)), f"Somehow this is creating empty values, with points as {points} and point as {point}"
    return points

def generateLandscapeDistriebution(row, d: float = 45, n: int = 20, k: int = 10,
                               angleRange: list[float] = [-15, -10, -5, 0, 5, 10, 15]) -> np.array:
    X, Y, d = row.X, row.Y, row.d
    angles = [(angle + (90-d)) * pi/180 for angle in angleRange]
    length_rng = [(exp(i * log(n+1)/k) - 1) * 1000 for i in range(1, k+1)]
    points = np.array([[(X + l*cos(angle), Y + l*sin(angle)) for angle in angles] for l in length_rng])
    assert not np.any(np.isnan(points)), f"Somehow this is creating empty values, with points as {points} and point as {(X, Y)}"
    points = flattenTo2dPoint(points)
    return points

def generateLandscapeDistribution2Sectors(row, d: float = 45, n: int = 20, k: int = 10,
                               angleRange: list[float] = [-15, -10, -5, 0, 5, 10, 15] + [-15+180, -10+180, -5+180, 0+180, 5+180, 10+180, 15+180]) -> np.array:
    X, Y, d = row.X, row.Y, row.d
    angles = [(angle + (90-d)) * pi/180 for angle in angleRange]
    length_rng = [(exp(i * log(n+1)/k) - 1) * 1000 for i in range(1, k+1)]
    points = np.array([[(X + l*cos(angle), Y + l*sin(angle)) for angle in angles] for l in length_rng])
    assert not np.any(np.isnan(points)), f"Somehow this is creating empty values, with points as {points} and point as {(X, Y)}"
    points = flattenTo2dPoint(points)
    return points

def generateLandscapeDistributionCircle(row, d: float = 45, n: int = 20, k: int = 10,
                               angleRange: list[float] = [a for a in range(-175, 185, 5)]) -> np.array:
    X, Y, d = row.X, row.Y, row.d
    angles = [(angle + (90-d)) * pi/180 for angle in angleRange]
    length_rng = [(exp(i * log(n+1)/k) - 1) * 1000 for i in range(1, k+1)]
    points = np.array([[(X + l*cos(angle), Y + l*sin(angle)) for angle in angles] for l in length_rng])
    assert not np.any(np.isnan(points)), f"Somehow this is creating empty values, with points as {points} and point as {(X, Y)}"
    points = flattenTo2dPoint(points)
    return points

def generateElevationDistribution(row, transform, index, elevation):
    points = row.landscape_points
    elevations = generateLandscapeElevationPoints(points, transform, index, elevation)
    return elevations
def findLandscapeElevationPickled(point: tuple[float], stationsPoints) -> float:
    x, y = point
    r, c = calcIndex(x, y)
    xi, yi = calcTransform(r, c)

    assert abs(x-xi) <= 20 and abs(y-yi) <= 20, "xi, yi not calculated correctly"

    if xi <= x and yi <= y:
        points_index = [(r,c), (r+1, c), (r, c-1), (r+1, c-1)]
    elif xi <= x and yi > y:
        points_index = [(r, c), (r+1, c), (r, c+1), (r, c+1)]
    elif xi > x and yi <= y:
        points_index = [(r, c), (r, c-1), (r-1, c), (r-1, c-1)]
    else:
        points_index = [(r, c), (r, c+1), (r-1, c), (r-1, c+1)]

    assert all([p in stationsPoints.keys() for p in points_index]), "Not all points are in stationsPoints.keys"

    point_values = [stationsPoints[p] for p in points_index]
    points_XY = [calcTransform(p[0], p[1]) for p in points_index]
    return bridgeElevation(point, points_XY, point_values)
# Returns the landscape elevation of a point based on the tif file
def findLandscapeElevation(point: tuple[float], transform, index, elevation):#tifPath: str = "D:/Skóli/lokaverkefni_vel/data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif", band = 1) -> float:
    """
    Args:
        point (tuple[float]): a x,y point representing the X, Y coordinates in ISN93 of a given point
        index: a function to retrive the index of given coordinates in the dataset
        transform: a function to retrieve coordinates of the given points in dataset
        tifPath (str): a string representing the dictionary where the quadTree indices pkl files are kept
        gridSpacing (float): the spacing of the elevation grid (that is 20m for given tif file)
    Returns:
        A float value that represents the elevation at the given point
    """
    height, width = elevation.shape
    point = np.array(point)
    py, px = index(*point)
    point_indexes = [(py, px), (py, px+1), (py, px-1), (py+1, px), (py-1, px), (py+1, px-1), (py-1, px+1), (py-1, px-1), (py+1, px+1)]
    point_indexes = [p for p in point_indexes if p[0] >= 0 and p[1] >= 0]
    point_indexes = [p for p in point_indexes if p[0] < height and p[1] < width]

    point_coordinates = [transform * p for p in point_indexes]
    point_values = [elevation[p] for p in point_indexes]
    
    if len(point_coordinates) < 2:
        return 0

    z = bridgeElevation(point, point_coordinates, point_values)

    return z if z > -1e20 else 0.0

def generateLandscapeElevation(point, transform, index, elevation):
    height, width = elevation.shape
    px, py = index(*point)
    
    point_indexes = [(py, px), (py, px+1), (py, px-1), (py+1, px), (py-1, px), (py+1, px-1), (py-1, px+1), (py-1, px-1), (py+1, px+1)]
    point_indexes = [p for p in point_indexes if p[0] >= 0 and p[1] >= 0]
    point_indexes = [p for p in point_indexes if p[0] < height and p[1] < width]

    point_coordinates = [transform * p for p in point_indexes]
    point_values = [elevation[p] for p in point_indexes]
    
    if len(point_coordinates) < 2:
        return 0

    z = bridgeElevation(point, point_coordinates, point_values)

    return z if z > -1e20 else 0.0
        
def findLandscapeElevationPoints(points: list[tuple[float]], transform, index, elevation) -> list[float]:
    """
    Args:
        points (list[tuple[float]]): a list of points to estimate the elevation of
        tifPath (str): a string representation of the path to GeoTiff file of elevation of Iceland
    Returns:
        a list of floats representing the elevavtion of points in a distribution
    """
    flatPoints = flattenTo2dPoint(points)  
    res = [findLandscapeElevation(point, transform, index, elevation) for point in flatPoints] #Pickled/Not Pickled

    return res

def generateLandscapeElevationPoints(points, transform, index, elevation):
    res = [generateLandscapeElevation(point, transform, index, elevation) for point in points]
    return res
        
def findLandscapeCoordinates(transform, r, c) -> tuple[list[float]]:
    """
    Args:
        transform: a transform function, given index, get isn93 coordinates
        r,c: the starting row, col (width, height (3,3))
    Returns:
        a list of elevations and coordinates for all points in the given window
    """
    coordinates = [transform * [r, c], transform * [r, c+1], transform * [r, c+2], transform * [r+1, c], transform * [r+1, c+1],
                transform * [r+1, c+2], transform * [r+2, c], transform * [r+2, c+1], transform * [r+2, c+2]]
    return coordinates

