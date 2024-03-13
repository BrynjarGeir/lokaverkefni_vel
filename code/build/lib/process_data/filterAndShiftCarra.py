from utils.transform import dropOutOfRange, addXYToGribDF
from utils.read import readCarraGRIBIntoDataFrame, getCarraIndicesToKeep
import os
import pandas as pd, numpy as np
from tqdm import tqdm
#import xarray as xr

def filterStrippedCarraFiles(CarraPath: str = "D:/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/", outputDirectory: str = "/mnt/e/StrippedCloserCarra/") -> None:
    files = [file for file in os.listdir(CarraPath) if file.endswith('.feather')]
    to_keep = getCarraIndicesToKeep()

    for file in tqdm(files, total = len(files)):
        filterCloserFile(file, outputDirectory, CarraPath, to_keep)

# Drop rows from Carra data in GRIB files and output to feather
def dropToFeather(GRIBPATH: str = "/mnt/e/CopiedCarraGRIB/", outputDirectory: str = "D:/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/") -> None: 
    files = os.listdir(GRIBPATH)

    files = [file for file in files if file.endswith(".grib")]

    to_keep = getCarraIndicesToKeep()

    for file in tqdm(files, total = len(files)):

        filterAndShiftFile(file, outputDirectory, GRIBPATH, to_keep)

# Split up function so as to be able to call it for a given file
def filterAndShiftFile(file: str, outputDirectory: str, GRIBPATH: str) -> None: #, to_keep: pd.Series) -> None:
    filename = file.split(".")[0] + ".feather"
    
    try:
        df = readCarraGRIBIntoDataFrame(os.path.join(GRIBPATH, file))
        #df = dropOutOfRange(df, to_keep)

        df = addXYToGribDF(df)

        outputPath = os.path.join(outputDirectory, filename)

        df.to_feather(outputPath)
        
    except KeyError as e:
        print(f"Not able to filter and shift {file}, with error message {e}.")

def filterCloserFile(file: str, outputDirectory: str, CarraPath: str, to_keep: pd.Series) -> None:
    try:
        df = pd.read_feather(os.path.join(CarraPath, file))
        if 'level_0' in df.columns and 'index' in df.columns:
            df.drop(['level_0', 'index'], axis = 1, inplace = True)
        df.set_index(['heightAboveGround', 'y', 'x'], inplace = True)

        df = df[df.index.isin(to_keep[to_keep].index)]
        df = addXYToGribDF(df)
        df.to_feather(os.path.join(outputDirectory, file), compression='lz4')
    except Exception as e:
        print(f"Not able to filter {file}, with error message {e}.")

def stripGribFiles(fileToKeepMatch: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/GRIB/2005-02-09-18_00.grib', directoryToCheck: str = '/mnt/e/CopiedCarraGrib/', outputDirectory: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/Feather/'):
    ds = xr.open_dataset(fileToKeepMatch)
    min_lat, max_lat = min(ds.latitude.values), max(ds.latitude.values)
    min_lon, max_lon = min(ds.longitude.values), max(ds.longitude.values)
       
    files = [file for file in os.listdir(directoryToCheck) if file.endswith('.grib')]

    already_read = [file.split('.')[0]+'.grib' for file in os.listdir(outputDirectory) if file.endswith('.feather')]

    files = [file for file in files if file not in already_read]

    for file in tqdm(files, total = len(files), desc = 'Going through GRIB files on e and saving as stripped feather in Feather directory'):

        ds = xr.open_dataset(os.path.join(directoryToCheck, file))
        df = ds.to_dataframe()
        df = df[(df.latitude >= min_lat) & (df.latitude <= max_lat) & (df.longitude >= min_lon) & (df.longitude <= max_lon)]
        df = addXYToGribDF(df)
        filename = file.split('.')[0] + '.feather'

        df.to_feather(os.path.join(outputDirectory, filename))

# Write feather Carra dataframes with multiindex heightAboveGround, y, x instead of latitude and longitude
# and keep latitude and longitude as columns
def setCarraFeatherIndexAsyx(index, width, height, directory: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/Feather/', outputDirectory: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/Feather/IndexUpdate/'):
    featherFileNames = [file for file in os.listdir(directory) if file.endswith('.feather')]

    for i, file in tqdm(enumerate(featherFileNames), total = len(featherFileNames)):
        try:
            df = pd.read_feather(os.path.join(directory, file))
            if df.index.names != ['heightAboveGround', 'latitude', 'longitude']:
                continue

            df['y'], df['x'] = np.vectorize(index)(df['X'], df['Y'])

            mask = (df['y'] >= 0) & (df['y'] < height) & (df['x'] >= 0) & (df['x'] < width)

            df = df[mask]

            df.reset_index(inplace = True)

            df.set_index(['heightAboveGround', 'y', 'x'], inplace = True)

            df.to_feather(os.path.join(outputDirectory, file))

        except Exception as e:
            print(e)
