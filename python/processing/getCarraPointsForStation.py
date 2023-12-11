import pickle
import pandas as pd
from pyqtree import Index
import pyarrow
from utils.transform import transformCoordinateSystems
from get_data.getCarraBasedOnVedur import 

def transfromStationCoordinates(station):
    lon, lat = station["lon"], station["lat"]

    station["lon"], station["lat"] = transformCoordinateSystems(lon, lat, 4326, 3057)

def generateStations(filepath):
    stations_file = pd.read_csv(filepath, encoding_errors = 'ignore', header=0)

    stations = {}

    for index, row in stations_file.iterrows():
        station = row["stod"]
        stations[station] = {"lon": -row["lengd"], "lat":row["breidd"]}

    return stations

def transformCoordinatesOfStations(stations):
    for station in stations:
        transfromStationCoordinates(stations[station])

    return stations


filepath = "/mnt/d/skóli/lokaverkefni_vel/data/stod.txt"

outputPath = "/mnt/d/skóli/lokaverkefni_vel/data/Vedurstofa/isn93StationCoordinates.pkl"

carraFeatherFilePath = "/mnt/e/skóli/lokaverkefni_vel/data/Carra/StrippedCarra/1993-11-28-18_00.feather"

stations = generateStations(filepath)

stations = transformCoordinatesOfStations(stations)


