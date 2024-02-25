from utils.util import findRelevantCarraFiles, allPresentFeatherFiles
from utils.bridging import bridgeSpatialCarra, bridgeCarraTemporal, findBoundingPoints
from utils.elevation import findLandscapeDistribution, findLandscapeElevationPoints, findLandscapeElevation
from utils.timeManipulation import createCarraNameBasedOnVedurTime
from tqdm import tqdm
from datetime import datetime
from affine import Affine
import rasterio, dill as pickle, os, pandas as pd, numpy as np

def bridgeForHeightLevel(bounding_points_prev: list, bounding_points_aft: list, prev_df: pd.DataFrame, aft_df: pd.DataFrame, X: float, Y: float, 
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
    prev_bounding_points = prev_df[bounding_points_prev]
    aft_bounding_points = aft_df[bounding_points_aft]

    prev_bridged = bridgeSpatialCarra(X, Y, prev_bounding_points, features_to_bridge)
    aft_bridged = bridgeSpatialCarra(X, Y, aft_bounding_points, features_to_bridge)

    prevTime, aftTime = prev_bounding_points["time"].iloc[0], aft_bounding_points["time"].iloc[0]

    prev_bridged = [prevTime] + prev_bridged
    aft_bridged = [aftTime] + aft_bridged
    
    bridged_features = [height_level, vedurDateTime, X, Y] + bridgeCarraTemporal(vedurDateTime, prev_bridged, aft_bridged)

    return bridged_features

def getDTXYDirFFg(row: pd.DataFrame) -> list:
    """
    Args:
        row (DataFrame) : A row from a dataframe
    Returns:
        The datetime, X,Y coordinates, direction, average wind speed and wind gust
    """
    return row.timi, row.X, row.Y, row.d, row.f, row.fg

def combineHeightLevels(cRow15: list, cRow150: list, cRow250: list, cRow500: list, point_elevation: float, landscape_elevation: list):
    """
    Args:
        cRow15 (list): a list representing a single row for given datetime, lat, lon at height_level = 15.0m
        cRow150 (list): a list representing a single row for given datetime, lat, lon at height_level = 150.0m
        cRow250 (list): a list representing a single row for given datetime, lat, lon at height_level = 250.0m
        cRow500 (list): a list representing a single row for given datetime, lat, lon at height_level = 500.0m
        landscape_bridgeD:/a list representing all the 70 (assuming 10 in dist and 7 angles) points elevation points in distribution
                            in direction of landscape
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
            wdir250, t250, ws250, pres250, wdir500, t500, ws500, pres500, point_elevation]

    combined.extend(landscape_elevation)

    return combined

def combineHeightLevelsCarraVedur(cRow15: list, cRow150: list, cRow250: list, cRow500: list):
    wdir15, t15, ws15, pres15 = cRow15[4], cRow15[5], cRow15[6], cRow15[7]
    wdir150, t150, ws150, pres150 = cRow150[4], cRow150[5], cRow150[6], cRow150[7]
    wdir250, t250, ws250, pres250 = cRow250[4], cRow250[5], cRow250[6], cRow250[7]
    wdir500, t500, ws500, pres500 = cRow500[4], cRow500[5], cRow500[6], cRow500[7]

    DT, lat, lon = cRow15[1:4]

    combined = [DT, lat, lon, wdir15, t15, ws15, pres15, wdir150, t150, ws150, pres150, 
            wdir250, t250, ws250, pres250, wdir500, t500, ws500, pres500]
    
    return combined
# This only expands on createCarraNameBasedOnVedurTime by using callCarra to source the files if not present
# If file(s) needs to be downloaded, then also needed to put in feather format like others and drop non relevant points
# The only real function of this function is to prepare the combination of Carra and Vedur, making sure that the carra files
# for both before and after are inplace

def combineAllVedurCarraLandscape(vedurPath: str, outputPath: str, columns = ['DateTime', 'lat', 'lon', 'wdir15', 't15', 'ws15', 'pres15', 'wdir150', 't150', 'ws150', 'pres150', 'wdir250', 't250', 'ws250', 'pres250', 'wdir500', 't500', 'ws500', 'pres500', 'elevation']) -> None:
    """
    Args:
        vedurPath (str): The string representation of the path to the location of the vedur feather file to be read and matched with Carra
                            Most likely the stripped 10 minute data
        outputPath (str): The string representation of the outputpath of the combined Vedurstofa and Carra data
        columns (list[str]): The column names of the ouput dataframe
    Returns:
        Nothing, but creates a new file with the combined Vedur and Carra information
    """
    #missing_data = []
    with open('D:/Skóli/lokaverkefni_vel/data/Carra/missing_data.pkl', 'rb') as f:
        missing_data = pickle.load(f)
        #print(type(missing_data), f"The number of missing data at 500,000 rows looked at is {len(missing_data)}")
    vedurDF = pd.read_feather(vedurPath)
    vedurDF = vedurDF.dropna(subset = ['timi', 'f', 'fg', 'stod', 'd', 'X', 'Y'])
    vedurDF['distance'] = (vedurDF.X**2 + vedurDF.Y**2)**0.5
    vedurDF.sort_values('distance', inplace = True)
    combinedRows = []
    columns = ["target"] + columns + ["Landscape_" + str(i) for i in range(70)]
    allPresentFeather = allPresentFeatherFiles()
    with rasterio.open("D:/Skóli/lokaverkefni_vel/data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif") as dataset:
        elevation = dataset.read(1)
        index = dataset.index
        transform = dataset.transform
    i = -1
    for row_number, row in tqdm(vedurDF.iterrows(), total = vedurDF.shape[0]):
        i += 1
        if not i % 10000:
            df = pd.DataFrame(combinedRows, columns = columns)
            df.to_feather(outputPath)
            with open('D:/Skóli/lokaverkefni_vel/data/Carra/missing_data.pkl', 'wb') as f:
                pickle.dump(missing_data, f)          
        try:
            vedurDateTime, X, Y, d, f, fg = getDTXYDirFFg(row)
            if np.isnan(d):
                continue
            cRow15, cRow150, cRow250, cRow500, point_elevation, landscape_elevation = combineVedurAndCarraLandscapeRow(vedurDateTime, X, Y, d, transform, index, elevation, allPresentFeather)
            if cRow15 == None:
                missing_data.append(vedurDateTime)
                continue
            aRow = combineHeightLevels(cRow15, cRow150, cRow250, cRow500, point_elevation, landscape_elevation)
            combinedRows.append([fg/f] + aRow)

        except Exception as e:
            print(f"Not able to get row {row_number}, with exception: {e}")
            try:
                vedurDateTime, _, _, _, _, _ = getDTXYDirFFg(row)
                missing_data.append(vedurDateTime)
            except Exception as e:
                print(f"Not able to get vedurDateTime for row {row_number}, with exception: {e}")

    df = pd.DataFrame(combinedRows, columns = columns)
    df.to_feather(outputPath)
    with open('D:/Skóli/lokaverkefni_vel/data/Carra/missing_data.pkl', 'wb') as f:
        pickle.dump(missing_data, f)

# Find create a single line in data for model
# Each line is one feature vector, given information about Carra and Vedur stations
def combineVedurAndCarraLandscapeRow(vedurDateTime: str, X: float, Y: float, d: float, transform, index, elevation, allPresentFeather: set, gridSpacing: float = 2500, features_to_bridge = ["wdir", "t", "ws", "pres"]) -> list:
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
    directory = 'D:/Skóli/lokaverkefni_vel/data/Carra/Feather'
    prev, aft = createCarraNameBasedOnVedurTime(vedurDateTime)
    if prev not in allPresentFeather or aft not in allPresentFeather:
        return None, None, None, None, None, None
    prev_df, aft_df = pd.read_feather(os.path.join(directory, prev)), pd.read_feather(os.path.join(directory, aft))

    if not all(feature in prev_df.columns for feature in features_to_bridge) or not all(feature in aft_df.columns for feature in features_to_bridge):
        return None, None, None, None, None, None

    bounding_points_prev = findBoundingPoints((X, Y), prev_df, index)
    bounding_points_aft = findBoundingPoints((X, Y), aft_df, index)
    landscapePoints = findLandscapeDistribution((X, Y), d)
    
    bP15_prev, bP150_prev, bP250_prev, bP500_prev = bounding_points_prev
    bP15_aft, bP150_aft, bP250_aft, bP500_aft = bounding_points_aft

    landscape_elevation = findLandscapeElevationPoints(landscapePoints, transform, index, elevation)
    point_elevation = findLandscapeElevation((X,Y), transform, index, elevation)

    bridged_15 = bridgeForHeightLevel(bP15_prev, bP15_aft, prev_df, aft_df, X, Y, features_to_bridge, vedurDateTime, height_level = 15)
    bridged_150 = bridgeForHeightLevel(bP150_prev, bP150_aft, prev_df, aft_df, X, Y, features_to_bridge, vedurDateTime, height_level = 150)
    bridged_250 = bridgeForHeightLevel(bP250_prev, bP250_aft, prev_df, aft_df, X, Y, features_to_bridge, vedurDateTime, height_level = 250)
    bridged_500 = bridgeForHeightLevel(bP500_prev, bP500_aft, prev_df, aft_df, X, Y, features_to_bridge, vedurDateTime, height_level = 500)

    return bridged_15, bridged_150, bridged_250, bridged_500, point_elevation, landscape_elevation

def getMissingCarra(feather_directory = "D:/Skóli/lokaverkefni_vel/data/Carra/StrippedCloserCarra/", vedurPath = "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stripped_10min.feather"):
    vedurDF = pd.read_feather(vedurPath)
    endOfCarraDT = datetime.strptime("2023-09-30 21:00:00", "%Y-%m-%d %H:%M:%S")
    for index, row in tqdm(vedurDF.iterrows(), total = vedurDF.shape[0]):
        if index < 3280:
            continue
        vedurDateTime, X, Y, d, f, fg = getDTXYDirFFg(row)
        vdt = datetime.strptime(vedurDateTime, "%Y-%m-%d %H:%M:%S")
        if vdt > endOfCarraDT:
            print(f"vedurDateTime {vedurDateTime} is out of range for Carra")
            continue
        prev, aft = findRelevantCarraFiles(vedurDateTime)

def resetFeatherFileIndex(feather_directory: str = "D:/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/") -> None:
    files = [file for file in os.listdir(feather_directory) if file.endswith('.feather')]
    for file in tqdm(files, total = len(files)):
        df = pd.read_feather(os.path.join(feather_directory, file))
        if 'level_0' in df.columns:
            df.drop('level_0', axis = 1)
        if isinstance(df.index, pd.MultiIndex):
            df = df.reset_index()
            df.to_feather(feather_directory + file)

#combineAllVedurCarraLandscape("D:/Skóli/lokaverkefni_vel/data/Vedurstofa/Stripped_25ms_10min.feather", "D:/Skóli/lokaverkefni_vel/data/combined-31-1-24.feather")