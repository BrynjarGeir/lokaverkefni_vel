from pyproj import Transformer
from utils.read import readCarraGRIBIntoDataframe
import pandas as pd
import pickle

# The data from Carra GRIB files seem to be shifted WGS84 for longitude
# That is it has same 0 at prime but the Carra go to 360 (no negative)
# So we create a function to transform to the same coordinates as we have in the elevation description
def transformCoordinatesFromShiftedWSG84ToISN93(lons, lats):
    transformer = Transformer.from_crs(4326, 3057, always_xy = True)

    return transformer.transform(lons, lats)

# As the coordinates are the same for each GRIB (that is in the same order) and there are many files,
# let's just get the coordinates once
def getCarraCoordinatesInISN93(points):
    lons, lats = [point[0] - 360 if point[0] > 180 else point[0] for point in points], [point[1] for point in points]
    nlons, nlats = transformCoordinatesFromShiftedWSG84ToISN93(lons, lats)
    return nlons, nlats

# Take all Carra Coordinates from example GRIB file and write to file the ISN93 coordinates
# This should be done after cutting excess points out of grib files (so as to have as few points as possible
# The output file is a feather file with only lat/long as the grid is the same for all GRIB files, we only need one set of
# coordinates, I should output to file the boolean list so that I can have that information to apply to other grib files
def rewriteCarraCoordinatesWithISN93Coordinates(df, output_filepath):

    points = list(zip(df['longitude'], df['latitude']))

    print(lons, lats)

    lons, lats = getCarraCoordinatesInISN93(points)

    result = [(lon, lat) for lon,lat in list(zip(lons, lats))]

    df = pd.DataFrame(result, columns = ['latitude', 'longitude'])

    df.to_feather(output_filepath)

def transformCoordinatesFromShiftedWSG84ToISN93WithinDF(df):
    lons, lats = df['longitude'], df['latitude']
    nlons, nlats = transformCoordinatesFromShiftedWSG84ToISN93(lons, lats)
    df['longitude'] = nlons
    df['latitude'] = nlats

    return df

def transformCoordinateSystems(lon, lat, old_coordinate_system, new_coordinate_system):
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

# Drop all points that are out of range as given by boolean list npoints
def dropOutOfRange(grib_df, npoints):
    return grib_df[npoints]

# Load index bool data so as to drop out of index for other GRIB files
def readIndexBool(path):
    with open(path, 'rb') as file:
        loaded_data = pickle.load(file)
    
    return loaded_data

#bbox = (-30.87, 59.96, -5.55, 69.59)