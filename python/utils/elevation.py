import os
from time import sleep
import numpy as np
import rasterio
from pyqtree import Index
import dill as pickle
from sklearn.cluster import AgglomerativeClustering
from scipy.interpolate import griddata
from tqdm.auto import trange
from utils.util import flattenList

def getLocationInDataset(point: tuple[float], gridsize: int = 20) -> tuple[int]:
    lon, lat = point
    x, y = (lon - 239980) // gridsize, (680000 - lat) // gridsize
    return int(x), int(y)

def getCoordinatesFromDatasetLocation(point: tuple[int], gridsize: int = 20) -> tuple[float]:
    x, y = point
    lon, lat = 239980 + x * gridsize, 680000 - y * gridsize
    return lon, lat

# I'll just assume 10 because otherwise you would have to always think of the shape
# Create the boundaries to divide the country into smaller more manageable sections (fit into memory)
# (220000,  300000, 800000, 700000) - þetta er það sem að ég prófaði eftir ISN93 map
# Það sem að er inni núna virðist 
def createBoundaries(boundary: tuple[float] = (239980,  310000, 760000, 680000)) -> list[list[tuple[float]]]:
    lat_min, lat_max = boundary[1], boundary[3]
    lon_min, lon_max = boundary[0], boundary[2]

    n, m = 40, 24

    space_lat = (lat_max - lat_min) / m
    space_lon = (lon_max - lon_min) / n

    res = [[(lon_min + space_lon * i, lat_max - space_lat * j, lon_min + space_lon * (i+1), lat_max - space_lat*(j+1)) for i in range(n)] for j in range(m)]
    res = flattenList(res)
    return res

# Check if given point is within given boundary
def isInBoundary(point, bbox):
    lat_min, lon_min, lat_max, lon_max = bbox
    x, y = point
    return lon_min <= x and x <= lon_max and lat_min <= y and y <= lat_max

# Given a tif file, boundary, a band to read from the tif file (and whether or not it's lat/long or long/lat)
# Create a quadtree as index from pyqtree to use as lookup to find points of interest close to a given point
# Þetta er allt isn93 svæðið og er óþarft: (-161615.71, -62312.13, 1248429.41, 1068116.03) tek minna út frá espg korti
# Og skipti því svo upp
# Þetta er er annað sem að ég prófaði þegar að ég var með width/height í öfugri röð (239980.0,  159980.0, 609980.0, 680000.0)
def createAndSaveQTree(tifPath: str = "/mnt/d/Skóli/lokaverkefni_vel/data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif",
                       outputDirectory: str = "/mnt/d/Skóli/lokaverkefni_vel/data/elevationPoints/QuadTreeIndices/", 
                boundary: tuple[float] = (239980, 310000, 760000, 680000), band: int = 1, gridSpacing: int = 20) -> None:
    
    bboxes = createBoundaries(boundary)

    # Just running for 1 until I get this right len(bboxes)
    for i in trange(len(bboxes), desc = f" At section", position = 0):

        with rasterio.open(tifPath) as dataset:
            transform = dataset.transform
            information = dataset.read(band)

        width, height = information.shape
        print(f"The shape of the dataset is {(width, height)}")
        
        cBound = bboxes[i]
        xi, yi, xj, yj = cBound
        startRow, startCol = getLocationInDataset((xi, yi))
        endRow, endCol = getLocationInDataset((xj, yj))

        index = Index(bbox = bboxes[i])
        for row in trange(startRow, endRow, desc=f" Populating section {i+1}", position=1, leave = False):
            for col in trange(startCol, endCol, desc=" Each row (shouldn't take any real time)", position = 2, leave = False):
                x, y = transform * (row, col)
                z = information[col, row]


                if z > -3.4e28:
                    bbox = (x-gridSpacing, y-gridSpacing, x+gridSpacing, y+gridSpacing)
                    index.insert((x, y, z), bbox)

        outputPath = outputDirectory + "index_" + str(i+1) + ".pkl"

                    
        with open(outputPath, "wb") as f:
            pickle.dump(index, f)
        del index

        sleep(1)
    
# Find notable points close to a given reference point
# The elevation index is the quadtree to be used as lookup
# The distance max is the maximum distance any point can be to be of interest for a reference point, like a mountain 100 km away
# is not of interest but one 5 km away is
# The elevation min filters out points that are too close in elevation to reference point to be of importance (not based on
# anything, just set at value, might need to be updated)
# This will output too many points as for example any point on top of a mountain, will be outputted, when we would really only
# want one
def findNoteablePoints(referencePoint, elevationIndex, elevationMin, gridSpacing: int = 20):
    x,y, referenceElevation = referencePoint
    bbox = (x-gridSpacing, y-gridSpacing, x+gridSpacing, y+gridSpacing)
    points_in_box = elevationIndex.intersect(bbox)
    notablePoints = []

    for point in points_in_box:
        x1, y1, elevation = point
        xDist, yDist = abs(x-x1), abs(y-y1)
        height_diff = elevation - referenceElevation
        if xDist <= gr and abs(height_diff) >= elevationMin:
            notablePoints.append((x1, y1, elevation, distance, height_diff))
    return notablePoints
# Groups points together using agglomerative clustering, this will group points together based on their location
# Then afterwards, we can select the extreme points from each group (i.e. the top of a mountain or the lowest part of a valley)
def groupPointsTogether(notablePoints, n_clusters = 5):
    agg_clustering = AgglomerativeClustering(n_clusters = n_clusters, linkage='ward')
    notablePoints_array = np.array([(point[0], point[1]) for point in notablePoints])
    cluster_labels = agg_clustering.fit_predict(notablePoints_array)

    grouped_points = {}

    for i, label in enumerate(cluster_labels):
        if label not in grouped_points:
            grouped_points[label] = []
        grouped_points[label].append(notablePoints[i])

    return grouped_points
# Select the extreme point in each group (that is where the difference in elevation is as high as possible) as a representative
def getExtremePoints(grouped_points, index):
    extreme_points = []
    for group in grouped_points:
        clist = grouped_points[group]
        extreme_value = max(clist, key=lambda x: abs(x[index]))
        extreme_points.append(extreme_value)
    return extreme_points

def bridge_extreme_points(extreme_points, carraIndex):
    return

def findLandscapeDistribution(point: tuple[float], d: float = 45, n: int = 20, k: int = 10,
                               angles: list[float] = [-15, -10, -5, 0, 5, 10, 15]) -> np.array:
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
    angles = [(angle + d) * pi/180 for angle in angles]
    length_rng = [(exp(i * log(n+1)/k) - 1) * 1000 for i in range(1, k+1)]
    points = np.array([[(x + l*cos(angle), y + l*sin(angle)) for angle in angles] for l in length_rng])        
    return points

def findLandscapeElevation(point: tuple[float], quadTreeDirectoryPath: str = "/mnt/d/Skóli/lokaverkefni_vel/data/elevationPoints", gridSpacing: float = 20) -> float:
    """
    Args:
        point (tuple[float]): a x,y point representing the latitude and longitude of a given point
        quadTreeDirectoryPath (str): a string representing the dictionary where the quadTree indices pkl files are kept
        gridSpacing (float): the spacing of the elevation grid (that is 20m for given tif file)
    Returns:
        A float value that represents the elevation at the given point
    """
    boundaryPoints = createBoundaries()
    i = -1
    for j in range(len(boundaryPoints)):
        isInBoundary(point, boundaryPoints[j])
        i = j
        break
    
    indexFilePath = os.path.join(quadTreeDirectoryPath, "index_" + str(i) + ".pkl")

    with open(indexFilePath, "rb") as f:
        index = pickle.load(f)
    
    y, x = point
    bbox = (y-gridSpacing, x - gridSpacing, y + gridSpacing, x + gridSpacing)
    points = index.intersect(bbox)
    values = [p[2] for p in points]
    coordsY, coordsX = [p[0] for p in points], [p[1] for p in points]
    res = griddata((coordsY, coordsX), values, [point], method = 'linear')
    return res

# Sanity check for created indices
def findMinMaxYInIndex(indexDirectory: str = "/mnt/d/Skóli/lokaverkefni_vel/data/elevationPoints"):
    boundaries = createBoundaries()
    outer_bbox = (-1e10, -1e10, 1e10, 1e10)
    for i, boundary in enumerate(boundaries):
        with open(os.path.join(indexDirectory, "index_" + str(i) + ".pkl"), "rb") as f:
            index = pickle.load(f)
        points = index.intersect(outer_bbox)
        y, x = [p[0] for p in points], [p[1] for p in points]

        print(f"For index section {i+1} the minimum y is {min(y)} and the maximum is {max(y)}")
        
#res = findLandscapeElevation((300000.0, 335960.0))

#print(f"For point {(300000.0, 335960.0)} the found elevation is {res}, when it should be {468.08588}")

def findBoundsTIF(tifPath: str = "/mnt/d/Skóli/lokaverkefni_vel/data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif"):
    with rasterio.open(tifPath) as dataset:
        transform = dataset.transform
        information = dataset.read(1)
    
    width, height = information.shape
    y_bounds, x_bounds = [1e100, -1e100], [1e100, -1e100]

    for row in trange(height, position = 0, desc=" Looping over rows"):
        for col in trange(width, position = 1, desc=" Looping over columns", leave = False):
            y,x = transform * (col, row)

            y_bounds[0], y_bounds[1] = min(y_bounds[0], y), max(y_bounds[1], y)
            x_bounds[0], x_bounds[1] = min(x_bounds[0], x), max(x_bounds[1], x)

    return y_bounds, x_bounds

#y_bounds, x_bounds = findBoundsTIF()

#print(f"The y_bounds are {y_bounds} and the x_bounds are {x_bounds}")

createAndSaveQTree()