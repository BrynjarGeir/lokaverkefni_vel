from pyproj import Transformer
import dill as pickle, rasterio, pandas as pd, numpy as np
from tqdm import tqdm
from affine import Affine

# The data from Carra GRIB files seem to be shifted WGS84 for longitude
# That is it has same 0 at prime but the Carra go to 360 (no negative)
# So we create a function to transform to the same coordinates as we have in the elevation description
def transformCoordinatesFromShiftedWGS84ToISN93(lons, lats):
    return None

# Transform from coordinate system WGS84 to ISN93 (lon/lat -> X/Y)
def transformWGS84ToISN93(lons, lats):
    transformer = Transformer.from_crs(4326, 3057, always_xy = True)

    return transformer.transform(lons, lats)

# Transform from coordinate system ISN93 to WGS84 (X/Y -> lon/lat)
def transformISN93ToWGS84(X, Y):
    transformer = Transformer.from_crs(3057, 4326, always_xy=True)
    return transformer.transform(X, Y)

# As the coordinates are the same for each GRIB (that is in the same order) and there are many files,
# let's just get the coordinates once
def getCarraCoordinatesInISN93(points: list[tuple]) -> tuple[list]:
    lons, lats = [point[0] - 360 if point[0] > 180 else point[0] for point in points], [point[1] for point in points]
    nlons, nlats = transformCoordinatesFromShiftedWGS84ToISN93(lons, lats)
    return nlons, nlats

def getVedurLonLatInISN93(lon: float, lat: float):
    transformer = Transformer.from_crs(4326, 3057, always_xy = True)
    return transformer.transform(-lon, lat)

# Take all Carra Coordinates from example GRIB file and write to file the ISN93 coordinates
# This should be done after cutting excess points out of grib files (so as to have as few points as possible
# The output file is a feather file with only lat/long as the grid is the same for all GRIB files, we only need one set of
# coordinates, I should output to file the boolean list so that I can have that information to apply to other grib files
def rewriteCarraCoordinatesWithISN93Coordinates(df, output_filepath):

    points = list(zip(df['longitude'], df['latitude']))

    X, Y = getCarraCoordinatesInISN93(points)

    result = [(x, y) for x,y in list(zip(X, Y))]

    df = pd.DataFrame(result, columns = ['X', 'Y'])

    df.to_feather(output_filepath)

def transformCoordinatesFromShiftedWSG84ToISN93WithinDF(df):
    lons, lats = df['longitude'], df['latitude']
    X, Y = transformCoordinatesFromShiftedWGS84ToISN93(lons, lats)
    df['X'] = X
    df['Y'] = Y

    return df

def transformCoordinateSystems(lon, lat, old_coordinate_system = 4326, new_coordinate_system = 3057):
    transformer = Transformer.from_crs(old_coordinate_system, new_coordinate_system, always_xy = True)
    return transformer.transform(lon, lat)
# A list of coordinates (in the original coordinate system assumed, just has to match the type of the boundary box)
# Returns a boolean list such that True values are inside range
# Then we can drop by index rows from every dataframe/grib file
# If output_filepath is given, then we also output the boolean list so as to apply it directly to other GRIB files
def findPointsInsideBoundary(bbox, points, output_filepath = None):
    npoints = [False for _ in range(len(points))]

    for index, point in enumerate(points):
        if insideBBox(bbox, point):
            npoints[index] = True
    
    if output_filepath:
        with open(output_filepath, 'wb') as file:
            pickle.dump(npoints, file)

    return npoints

# Check if given point is within a given boundary box
def insideBBox(bbox, point):
    x1, y1, x2, y2 = bbox
    x, y = point

    if x > 180:
        x -= 360
    
    return (x1 <= x and x <= x2) and (y1 <= y and y <= y2)

def getXYStation(station: str, filePath: str = 'D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stodvar.pkl'):
    with open(filePath, 'rb') as file:
        stations = pickle.load(file)
    return stations[station]
# Drop all points that are out of range for a given station
def dropOutOfRange(grib_df: pd.DataFrame, to_keep: pd.Series):
    return grib_df[to_keep]

def addXYToGribDF(grib_df: pd.DataFrame) -> pd.DataFrame:
    # These two lines just depend on whether lon/lat are index or columns
    lons, lats = grib_df.index.get_level_values('longitude'), grib_df.index.get_level_values('latitude')
    #lons, lats = grib_df.longitude, grib_df.latitude
    
    X, Y = transformCoordinatesFromShiftedWGS84ToISN93(lons, lats)

    grib_df['X'] = X
    grib_df['Y'] = Y

    return grib_df

def readIndexBool(path: str):
    with open(path, 'rb') as f:
        res = pickle.load(f)
    return res

def getPointsInGrid(center, index, elevation, maxX, maxY, minPoints: int = 1002):
    x, y = center
    row, col = index(x, y)
    elevations = {}
    e = elevation[row, col]
    elevations[(row, col)] = e

    for i in range(-minPoints, minPoints+1):
        if row + i < 0: continue
        if row + i >= maxX: break
        for j in range(-minPoints, minPoints+1):
            if col + j < 0: continue
            if col + j >= maxY: break
            r, c = row + i, col + j
            e = elevation[r, c]
            elevations[(r, c)] = e
    return elevations

# Read all elevation points in 20km grid around each station so as to not having to read the whole file so often
def getElevationPoints(tifPath: str = "D:/Skóli/lokaverkefni_vel/data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif", stationsPath: str = "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stationsLonLatXY.pkl", outputDirectory: str = "D:/Skóli/lokaverkefni_vel/data/elevationPoints/pointDist4/", orderPath: str = 'D:/Skóli/lokaverkefni_vel/data/elevationPoints/stationsOrder.csv', elevationPath: str = 'D:/Skóli/lokaverkefni_vel/data/elevationPoints/elevation.npy', splitInto: int = 10) -> None:
    with open(stationsPath, 'rb') as f:
        stations = pickle.load(f)
    order = pd.read_csv(orderPath)
    order = list(order.values)
    order = [o[0] for o in order]
    with rasterio.open(tifPath) as dataset:
        index = dataset.index
    avg_size = len(order) // splitInto
    remainder = len(order) % splitInto
    stationsList = list(order)

    elevation = np.load(elevationPath)
    width, height = elevation.shape
    
    #expectedSize = os.path.getsize('D:/Skóli/lokaverkefni_vel/data/elevationPoints/pointDist/1395-1474.pkl')

    splitStations = [stationsList[i * avg_size + min(i, remainder):(i + 1) * avg_size + min(i + 1, remainder)] for i in range(splitInto)]

    for sublist in tqdm(splitStations, total = len(splitStations)):
        outputPath = outputDirectory + str(sublist[0]) + "-" + str(sublist[-1]) + ".pkl"
        #cFileSize = os.path.getsize(outputPath)
        #if expectedSize == cFileSize:
        #    continue
        pointsOfInterest = {}

        for station in tqdm(sublist, total = len(sublist)):
            points_in_grid = getPointsInGrid(stations[station][2:], index, elevation, width, height)
            pointsOfInterest.update(points_in_grid)
            cX, cY = stations[station][2:]
            cR, cC = index(cX, cY)
            assert((cR, cC) in points_in_grid.keys())
        
        with open(outputPath, "wb") as f:
            pickle.dump(points_in_grid, f)