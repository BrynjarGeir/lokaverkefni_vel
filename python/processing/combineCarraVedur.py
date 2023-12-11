from utils.util import findRelevantCarraFiles
from utils.bridging import bridgeSpatialCarra, bridgeCarraTemporal, findBoundingPoints
from utils.elevation import findLandscapeDistribution, findLandscapeElevation
import pandas as pd
from tqdm import tqdm
from datetime import datetime
import os
import pickle

def bridgeForHeightLevel(bounding_points: list, prev_df: pd.DataFrame, aft_df: pd.DataFrame, lat: float, lon: float, 
                         features_to_bridge: list, vedurDateTime: str, height_level: float) -> list[float]:
    """
    Args:
        bounding_points (list): a list of the four bounding points from Carra that bound the Vedurstofa measurement at lat, lon
        prev_df (pd.DataFrame): the Carra grid at the 3 hour interval before the actual measurement
        aft_df (pd.DataFrame): the Carra grid at the 3 hour interval after the actual measurement
        lat (float): The latitude of the measurement of Vedurstofa
        lon (float): The longitude of the measurement of Vedurstofa
        features_to_bridge (list): The named features to be bridged as there is more columns in the dataframes than I want to bridge
        vedurDateTime (str): a string that represents the DateTime of the measurement by Vedurstofa
        height_level (float): The height level we are looking at for this one (because the bounding points are selected based on lat/lon/height_level)
    Returns:
        Returns the bridged features, for a given lat/lon/height in a list

    """
    prev_bounding_points = prev_df.iloc[bounding_points.values]
    aft_bounding_points = aft_df.iloc[bounding_points.values]

    prev_bridged = bridgeSpatialCarra(lat, lon, prev_bounding_points, features_to_bridge)
    aft_bridged = bridgeSpatialCarra(lat, lon, aft_bounding_points, features_to_bridge)

    prevTime, aftTime = prev_bounding_points["time"].iloc[0], aft_bounding_points["time"].iloc[0]

    prev_bridged = [prevTime] + prev_bridged
    aft_bridged = [aftTime] + aft_bridged

    bridged_features = [height_level, vedurDateTime, lat, lon] + bridgeCarraTemporal(vedurDateTime, prev_bridged, aft_bridged)

    return bridged_features

def getDTLatLonDir(row: pd.DataFrame) -> list:
    """
    Args:
        row (DataFrame) : A row from a dataframe
    Returns:
        The datetime, latitude and longitude.
    """
    return row['timi'], row['lat'], row['lon'], row['d']

def combineHeightLevels(cRow15: list, cRow150: list, cRow250: list, cRow500: list, landscape_elevation: list):
    """
    Args:
        cRow15 (list): a list representing a single row for given datetime, lat, lon at height_level = 15.0m
        cRow150 (list): a list representing a single row for given datetime, lat, lon at height_level = 150.0m
        cRow250 (list): a list representing a single row for given datetime, lat, lon at height_level = 250.0m
        cRow500 (list): a list representing a single row for given datetime, lat, lon at height_level = 500.0m
        landscape_bridged: a nested list representing all the 70 (assuming 10 in dist and 7 angles) points bridged
            in direction of wind representing the landscape
    Returns:
        A single list containing all the relevant information from each height level that will the be a single row
        in the dataset to be used with model (additional information maybe added or information removed, derivatives like Ri, N
        might be added)
    """

    wdir15, t15, ws15, pres15 = cRow15[4], cRow15[5], cRow15[6], cRow15[7]
    wdir150, t150, ws150, pres150 = cRow150[4], cRow150[5], cRow150[6], cRow150[7]
    wdir250, t250, ws250, pres250 = cRow250[4], cRow250[5], cRow250[6], cRow250[7]
    wdir500, t500, ws500, pres500 = cRow500[4], cRow500[5], cRow500[6], cRow500[7]

    DT, lat, lon = cRow15[1:4]

    combined = [DT, lat, lon, wdir15, t15, ws15, pres15, wdir150, t150, ws150, pres150, 
            wdir250, t250, ws250, pres250, wdir500, t500, ws500, pres500]
    
    flatten = [item for sub in landscape_elevation for item in sub]


    combined.extend(flatten)

    return combined

# This only expands on createCarraNameBasedOnVedurTime by using callCarra to source the files if not present
# If file(s) needs to be downloaded, then also needed to put in feather format like others and drop non relevant points
# The only real function of this function is to prepare the combination of Carra and Vedur, making sure that the carra files
# for both before and after are inplace

def combineAllVedurCarraLandscape(vedurPath: str, outputPath: str, columns = ['DateTime', 'lat', 'lon', 'wdir15', 't15', 'ws15', 'pres15', 'wdir150', 't150', 'ws150', 'pres150', 'wdir250', 't250', 'ws250', 'pres250', 'wdir500', 't500', 'ws500', 'pres500']) -> None:
    """
    Args:
        vedurPath (str): The string representation of the path to the location of the vedur feather file to be read and matched with Carra
                            Most likely the stripped 10 minute data
        outputPath (str): The string representation of the outputpath of the combined Vedurstofa and Carra data
        columns (list[str]): The column names of the ouput dataframe
    Returns:
        Nothing, but creates a new file with the combined Vedur and Carra information
    """
    vedurDF = pd.read_feather(vedurPath)
    combinedRows = []
    columns = columns + ["Landscape_" + str(i) for i in range(70)]


    for index, row in tqdm(vedurDF.iterrows(), total = vedurDF.shape[0]):
        try:
            vedurDateTime, lat, lon, d = getDTLatLonDir(row)
            cRow15, cRow150, cRow250, cRow500, landscape_elevation = combineVedurAndCarraRow(vedurDateTime, lat, lon, d)
            aRow = combineHeightLevels(cRow15, cRow150, cRow250, cRow500, landscape_elevation)
            combinedRows.append(aRow)
        except Exception as e:
            print(f"Not able to get row {index}, with exception: {e}")
    df = pd.DataFrame(combinedRows, columns = columns)
    df.to_feather(outputPath)

# Find create a single line in data for model
# Each line is one feature vector, given information about Carra and Vedur stations
def combineVedurAndCarraRow(vedurDateTime: str, lat: float, lon: float, d: float = 45, gridSpacing: float = 2500, features_to_bridge = ["wdir", "t", "ws", "pres"]) -> list:
    """
    Args:
        vedurDateTime (str): The string representation of the measurement by Vedurstofa
        lat (float): the latitude of the Vedurstofa measurement (most likely in ISN93)
        lon (float): the longitude of the Vedurstofa measurement (most likely in ISN93)
        gridSpacing (float): The gridspacing of the rectangular grid by Carra (the resolution is 2.5km)
        features_to_bridge (list[str]): A string list of the features that need to be bridged
    Returns:
        Returns a a list for each height level [15, 150, 250, 500] of bridged features, both spatially and temporally
    """
    prev, aft = findRelevantCarraFiles(vedurDateTime)
    prev_df, aft_df = pd.read_feather(prev), pd.read_feather(aft)
    bounding_points = findBoundingPoints((lat, lon), prev_df)
    landscapePoints = findLandscapeDistribution((lat, lon), d)
    landscape_elevation = [[findLandscapeElevation(point) for point in row] for row in landscapePoints]

    bP15, bP150, bP250, bP500 = bounding_points

    bridged_15 = bridgeForHeightLevel(bP15, prev_df, aft_df, lat, lon, features_to_bridge, vedurDateTime, height_level = 15)
    bridged_150 = bridgeForHeightLevel(bP150, prev_df, aft_df, lat, lon, features_to_bridge, vedurDateTime, height_level = 150)
    bridged_250 = bridgeForHeightLevel(bP250, prev_df, aft_df, lat, lon, features_to_bridge, vedurDateTime, height_level = 250)
    bridged_500 = bridgeForHeightLevel(bP500, prev_df, aft_df, lat, lon, features_to_bridge, vedurDateTime, height_level = 500)

    return bridged_15, bridged_150, bridged_250, bridged_500, landscape_elevation

def getMissingCarra(feather_directory = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/", resetFilePath = "/mnt/d/Skóli/lokaverkefni_vel/needs_to_reset_index.txt", vedurPath = "/mnt/d/Skóli/lokaverkefni_vel/data/Vedurstofa/stripped_10min.feather"):
    vedurDF = pd.read_feather(vedurPath)
    endOfCarraDT = datetime.strptime("2023-09-30 21:00:00", "%Y-%m-%d %H:%M:%S")
    for index, row in tqdm(vedurDF.iterrows(), total = vedurDF.shape[0]):
        if index < 3280:
            continue
        vedurDateTime, lat, lon, d = getDTLatLonDir(row)
        vdt = datetime.strptime(vedurDateTime, "%Y-%m-%d %H:%M:%S")
        if vdt > endOfCarraDT:
            print(f"vedurDateTime {vedurDateTime} is out of range for Carra")
            continue
        prev, aft = findRelevantCarraFiles(vedurDateTime)

def resetFeatherFileIndex(feather_directory: str = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/") -> None:
    files = [file for file in os.listdir(feather_directory) if file.endswith('.feather')]
    for file in tqdm(files, total = len(files)):
        df = pd.read_feather(os.path.join(feather_directory, file))
        if 'level_0' in df.columns:
            df.drop('level_0', axis = 1)
        if isinstance(df.index, pd.MultiIndex):
            df = df.reset_index()
            df.to_feather(feather_directory + file)
        
#resetFeatherFileIndex()

combineAllVedurCarraLandscape("/mnt/d/Skóli/lokaverkefni_vel/data/Vedurstofa/stripped_10min.feather", "/mnt/d/Skóli/lokaverkefni_vel/data/combinedTest.feather")
