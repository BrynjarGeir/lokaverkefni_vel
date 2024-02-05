from pyqtree import Index
import pickle
import os
import pandas as pd
from math import sqrt
from time import time

# Read in given feather file to a dataframe with given station coordinates
# Find the index of all points that are close enough to bee needed
# Keep in mind that all the coordinates are supposedly in meters
def findRelevantPoints(filepath, station, max_dist = 20000):

    df = pd.read_feather(filepath)

    relevantPointsIndex = []

    st_lon, st_lat = station['lon'], station['lat']

    for i, row in df.iterrows():
        lon, lat = abs(row['longitude']-st_lon), abs(row['latitude']-st_lat)
        if sqrt(lon**2 + lat**2) <= max_dist:
            relevantPointsIndex.append(i)

    return relevantPointsIndex
        
# Call findRelevantPoints for all stations, this is done to drop lines
# From all feather files so as to shrink the data
def findAllRelevantPoints(filepath, outputPathAllRelevant, stations):
    allIndices = set()
    n, i = len(stations.keys()), 1
    start = time()
    last = start

    for station in stations:
        cRelevant = findRelevantPoints(filepath, stations[station])
        allIndices.update(cRelevant)
        ctime = time()
        print(f"Finished update number {i} of {n}.")
        print(f"This took {ctime-last} seconds.")
        print(f"Total time elapsed since starting is {(ctime - start) / 60} minutes.")
        print(f"This would indicate that the total time would be around {(ctime-start) * n / (i * 60*60)} hours.")
        last = ctime
        i += 1
    with open(outputPathAllRelevant, "wb") as f:
        pickle.dump(allIndices, f)
    return allIndices

# Drop all the indices that are not in allIndices for a single feather file
def dropNonRelevant(filepath, indices):
    df = pd.read_feather(filepath)

    df = df.drop(indices)

    df.to_feather("/mnt/e/test.feather")

def dropAllNonRelevant(indices, directory = "D:/Skóli/lokaverkefni_vel/data/Carra/CarraStripped/", extension = ".feather"):
    files = [file for file in os.listdir(directory) if file.endswith(extension)]
    for file in files:
        filepath = os.path.join(directory, file)
        dropNonRelevant(filepath, indices)

def getNonrelevant(relevantIndices, filepath):
    df = pd.read_feather(filepath)
    return list(set(df.index) - set(relevantIndices))

def dropAllNonRelevantFeather(stationsPath = "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/isn93StationCoordinates.pkl",
                               directory = "D:/Skóli/lokaverkefni_vel/data/Carra/CarraStripped/",
                               filepath = 'D:/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/1993-11-28-18_00.feather'):
    with open(stationsPath, "rb") as f:
        stations = pickle.load(f)
    relevantIndices = findAllRelevantPoints(filepath, "D:/Skóli/lokaverkefni_vel/data/Carra/relevantIndices.pkl", stations)
    nonRelevantIndices = getNonrelevant(relevantIndices, filepath)
    dropAllNonRelevant(nonRelevantIndices)


findAllRelevantPoints('D:/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/1993-11-28-18_00.feather', "D:/Skóli/lokaverkefni_vel/data/Carra/relevantIndices.pkl")
stationsPath = "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/isn93StationCoordinates.pkl"
with open(stationsPath, "rb") as f:
    stations = pickle.load(f)
