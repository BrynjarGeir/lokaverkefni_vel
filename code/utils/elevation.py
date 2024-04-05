import numpy as np
from math import exp, log, cos, sin, pi
from utils.interpolate import bridgeElevation
from utils.util import flattenTo2dPoint

def generateLandscapeDistribution(row, d: float = 45, n: int = 20, k: int = 10,
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

def generateElevationDistribution(row, transform, index, elevation):
    points = row.landscape_points
    elevations = generateLandscapeElevationPoints(points, transform, index, elevation)
    return elevations

def addPointElevation(row, transform, index, elevation):
    X, Y = row.X, row.Y
    return findLandscapeElevation((X, Y), transform, index, elevation)