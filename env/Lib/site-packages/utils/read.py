#import xarray as xr<
import pandas as pd
from utils.transform import getCarraCoordinatesInISN93, addXYToGribDF
import dill as pickle
from tqdm import tqdm

# Reads a grib file into a dataset with XARRAY
def readCarraGRIBIntoDataFrame(filepath: str) -> pd.DataFrame:
    ds = xr.open_dataset(filepath, engine = 'cfgrib')#, backend_kwargs={'filter_by_keys':{'name':variables_to_read}})
    df = ds.to_dataframe()
    ds.close()
    return df

# Returns the 1d dataframe (series) that has the information about which data to keep track of from the GRIB files
# This takes a 40 km square around each station (for any time) and keeps those
# This reduces the data to around 1.6% of what it was but obviously could be reduced much further if you take into account the time aspect
def getCarraIndicesToKeep(toKeepPath: str = "D:/Skóli/lokaverkefni_vel/data/Carra/toKeep.feather") -> pd.Series:
    to_keep = pd.read_feather(toKeepPath)
    return to_keep['to_keep']
# Creates a series/1d dataframe that keeps track of which rows to keep of the grib data (so as to only have points close to weather stations)
def createToKeepFile(toKeepPath: str = "D:/Skóli/lokaverkefni_vel/data/Carra/toKeep.feather", stationsXYPath: str = "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stationsXY.pkl", gribExample: str = "/mnt/e/CopiedCarraGRIB/1993-11-28-18_00.grib", rnge: int = 20e3) -> None:
    grib_df = readCarraGRIBIntoDataFrame(gribExample)
    grib_df = addXYToGribDF(grib_df)
    with open(stationsXYPath, 'rb') as file:
        stations = pickle.load(file)

    to_keep = pd.Series(False, index = grib_df.index)

    for station in tqdm(stations, total = len(stations.keys())):
        x, y = stations[station]
        indsX = grib_df.X.between(x-rnge, x+rnge)
        indsY = grib_df.Y.between(y-rnge, y+rnge)
        current = indsX & indsY

        to_keep |= current
    print(f"Number of True/False in to_keep is: {to_keep.value_counts()}")
    outputDF = pd.DataFrame({'to_keep': to_keep})

    outputDF.to_feather(toKeepPath)

# Creates a pickled object that tracks the locations of weather stations in a dictionary keyed by the id of each station
# Coordinates are in XY
def createStationsDict(stationsPath: str = "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stationsLonLatXY.pkl", stodPath: str = "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stod.txt") -> None:
    stations = {}
    encoding = 'ISO-8859-1'
    with open(stodPath, 'r', encoding=encoding) as f:
        lines = [line.strip() for line in f.readlines()][1:]
    
    for line in lines:
        station = line.split(',')
        stod, breidd, lengd = int(station[0]), float(station[2]), float(station[3])
        stations[stod] = (-lengd, breidd)

    for stod in tqdm(stations, total = len(stations.keys())):
        x, y = getCarraCoordinatesInISN93([stations[stod]])
        lengd, breidd = stations[stod]
        stations[stod] = (lengd, breidd, x[0], y[0])

    with open(stationsPath, 'wb') as f:
        pickle.dump(stations, f)