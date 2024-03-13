import dill as pickle
from affine import Affine
import numpy as np, os, rasterio, pandas as pd

transformPath = 'D:/Skóli/lokaverkefni_vel/data/elevationPoints/transform.pkl'

def recreateAffine(a, b, c, d, e, f, g, h, i):
        return Affine(a, b, c, d, e, f, g, h, i)
# To be able to store the transform function
class CustomAffinePickler:
    def __reduce__(self):
        return (recreateAffine, (self.a, self.b, self.c, self.d, self.e, self.f, self.g, self.h, self.i))
# Returns a transform Affine (matrix) that when multiplied with a given index row, column spits out the coordinate at that index
def getTransform(transformPath: str = transformPath) -> Affine:
    with open(transformPath, 'rb') as f:
        transform = pickle.load(f)
    return transform
# Get an index function that returns the index row, column of a coordinate in the tif file
def getIndex(tifPath: str = "D:/Skóli/lokaverkefni_vel/data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif"):
    with rasterio.open(tifPath) as dataset:
        index = dataset.index
    return index

def calcIndex(x, y, minX: float = 239980, maxY: float = 680000, width = 18501, height = 26002):
    xi = (x//20) * 20
    yi = (y//20) * 20
    xi = xi - minX
    yi = maxY - yi
    xi //= 20
    yi //= 20
    if xi >= width or xi < 0:
        xi = -1
    if yi < 0 or yi >= height:
        yi = -1
    xi, yi = int(xi), int(yi)
    return xi, yi

def calcTransform(r, c, minX: float = 239980, maxY: float = 680000, spacing = 20):
    x = minX + r * spacing
    y = maxY - c * spacing

    return x, y

# To be able to split up tif file for memory purposes, this method will return the list (sublists) describing how the stations were split
def getStationsList(stationsPath: str = "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stationsLonLatXY.pkl", splitInto: int = 10):
    order = pd.read_csv('D:/Skóli/lokaverkefni_vel/data/elevationPoints/stationsOrder.csv')
    order = list(order.values)
    order = [o[0] for o in order]
    avg_size = len(order) // splitInto
    remainder = len(order) % splitInto
    stationsList = order

    splitStations = [stationsList[i * avg_size + min(i, remainder):(i + 1) * avg_size + min(i + 1, remainder)] for i in range(splitInto)]
    return splitStations
#Returns the opened pkl file that contains points relevant to station
def getElevationFile(station: int):
    stationsList = getStationsList()
    for sublist in stationsList:
        if station in sublist:
            sblst = sublist
    filePath = 'D:/Skóli/lokaverkefni_vel/data/elevationPoints/pointDist3/' + str(sblst[0]) + '-' + str(sblst[-1]) + '.pkl'
    with open(filePath, 'rb') as f:
        stationsPoints = pickle.load(f)
    return stationsPoints
        
def getElevationBand(tifPath: str = "D:/Skóli/lokaverkefni_vel/data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif"):
    with rasterio.open(tifPath) as dataset:
        elevation = dataset.read(1)
        shape = dataset.shape
    return elevation, shape
