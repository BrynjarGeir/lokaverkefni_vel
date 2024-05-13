import numpy as np, rasterio, dill as pickle, os
from math import exp, log, cos, sin, pi
from utils.util import flattenList
from utils.util import getTopLevelPath
from tqdm.notebook import tqdm
from datetime import date

folder_path =  getTopLevelPath() + 'data/'
elevation_path = folder_path + "Elevation/IslandsDEMv1.0_20x20m_isn93_zmasl.tif"
stationsLonLatXY_path = folder_path + 'Measured/stationsLonLatXY.pkl'
stationElevationCircles_path = folder_path + 'Elevation/' + max([file for file in os.listdir(folder_path + 'Elevation/') if file.endswith('.pkl') and file.startswith('elevation_circles_')], key = lambda f: os.path.getmtime(folder_path + 'Elevation/' + f))
stationElevations_path = folder_path + 'Elevation/' + max([file for file in os.listdir(folder_path + 'Elevation/') if file.endswith('.pkl') and file.startswith('station_elevations_')], key = lambda f: os.path.getmtime(folder_path + 'Elevation/' + f))
today = date.today().strftime("%Y-%m-%d")


with rasterio.open(elevation_path) as dataset:
    elevation = dataset.read(1)
    index = dataset.index
    transform = dataset.transform

transform = np.array(transform).reshape(3, 3)

def generatLandscapeElevationsCirclesForStations(stationsLonLatXY_path = stationsLonLatXY_path):
    with open(stationsLonLatXY_path, 'rb') as f:
        stationsLonLatXY = pickle.load(f)
    elevations_circles = {}
    for station in tqdm(stationsLonLatXY.keys(), total = len(stationsLonLatXY.keys())):
        landscape = generateLandscapeDistributionCircle((*stationsLonLatXY[station][2:], None))
        e = generateLandscapeElevationPoints(landscape)
        elevations_circles[station] = e
    outputpath = getTopLevelPath() + f'data/Elevation/elevation_circles_{today}.pkl'
    with open(outputpath, 'wb') as f:
        pickle.dump(elevations_circles, f)

def generateStationElevations(stationsLonLatXY_path = stationsLonLatXY_path):
    with open(stationsLonLatXY_path, 'rb') as f:
        stationsLonLatXY = pickle.load(f)
    station_elevations = {}
    for station in tqdm(stationsLonLatXY.keys(), total = len(stationsLonLatXY.keys())):
        e = generateLandscapeElevation(stationsLonLatXY[station][2:])
        station_elevations[station] = e
    outputpath = getTopLevelPath() + f'data/Elevation/station_elevations_{today}.pkl'
    with open(outputpath, 'wb') as f:
        pickle.dump(station_elevations, f)

def getStationElevations(stationElevations_path = stationElevations_path):
    with open(stationElevations_path, 'rb') as f:
        res = pickle.load(f)
    return res

def getStationElevationCircles(stationElevationCircles_path = stationElevationCircles_path):
    with open(stationElevationCircles_path, 'rb') as f:
        res = pickle.load(f)
    return res

def generateLandscapeDistribution1Sector(XYd, n: int = 20, k: int = 10,
                               angleRange: list[float] = [-15, -10, -5, 0, 5, 10, 15]) -> np.array:
    X, Y, d = XYd
    angles = [(angle + (90-d)) * pi/180 for angle in angleRange]
    length_rng = [(exp(i * log(n+1)/k) - 1) * 1000 for i in range(1, k+1)]
    points = np.array([[(X + l*cos(angle), Y + l*sin(angle)) for angle in angles] for l in length_rng])
    assert not np.any(np.isnan(points)), f"Somehow this is creating empty values, with points as {points} and point as {(X, Y)}"
    points = flattenList(points)
    return points

def generateLandscapeDistribution2Sectors(XYd, n: int = 20, k: int = 10,
                               angleRange: list[float] = [-15, -10, -5, 0, 5, 10, 15] + [-15+180, -10+180, -5+180, 0+180, 5+180, 10+180, 15+180]) -> np.array:
    X, Y, d = XYd
    angles = [(angle + (90-d)) * pi/180 for angle in angleRange]
    length_rng = [(exp(i * log(n+1)/k) - 1) * 1000 for i in range(1, k+1)]
    points = np.array([[(X + l*cos(angle), Y + l*sin(angle)) for angle in angles] for l in length_rng])
    assert not np.any(np.isnan(points)), f"Somehow this is creating empty values, with points as {points} and point as {(X, Y)}"
    points = flattenList(points)
    return points

def generateLandscapeDistributionCircle(XYd, d: float = 45, n: int = 20, k: int = 10,
                               angleRange: list[float] = [a for a in range(-175, 185, 5)]) -> np.array:
    X, Y, _ = XYd
    angles = [(angle + (90-d)) * pi/180 for angle in angleRange]
    length_rng = [(exp(i * log(n+1)/k) - 1) * 1000 for i in range(1, k+1)]
    points = np.array([[(X + l*cos(angle), Y + l*sin(angle)) for angle in angles] for l in length_rng])
    assert not np.any(np.isnan(points)), f"Somehow this is creating empty values, with points as {points} and point as {(X, Y)}"
    points = flattenList(points)
    return points

def generateLandscapeElevation(point: tuple[float]):
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
    # Check if the point falls within the bounding box of the elevation dataset
    py, px = index(*point)    
    # Get the elevation values for the surrounding points
    point_values = elevation[py:py+2, px:px+2].flatten()
    z = np.mean(point_values)
    return z if z > -1e20 else 0.0


def generateLandscapeElevationPoints(points):
    return [generateLandscapeElevation(point) for point in points]

def addPointElevation(XYd):
    X, Y, _ = XYd
    return generateLandscapeElevation((X, Y))