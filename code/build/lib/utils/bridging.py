from datetime import datetime
import numpy as np, pandas as pd
from utils.util import getDistances, getWeights

def findBoundingPoints(point: tuple[float], df: pd.DataFrame, tolerance: float = 3e3) -> list:
    """
    Args:
        df (DataFrame): a dataframe that contains all the griddata from Carra files
        gridSpacing (float): the distance between numbers in the Carra grid (2500 m)
        point (tuple(float)): the given point from Vedur data
    Returns:
        A index list of group of points (4, except given point matches grid point (unlikely)) that bound the given vedur
        data point. That is the indices of the four relevant points.
    """
    X, Y = point
    x_condition = (df.X >= X- tolerance) & (df.X <= X + tolerance)#df.index.get_level_values('x').isin([x, x+1, x-1])
    y_condition = (df.Y >= Y - tolerance) & (df.Y <= Y + tolerance)#df.index.get_level_values('y').isin([y, y+1, y-1])
    height_condition_15 = df.index.get_level_values('heightAboveGround') == 15.0
    height_condition_150 = df.index.get_level_values('heightAboveGround') == 150.0
    height_condition_250 = df.index.get_level_values('heightAboveGround') == 250.0
    height_condition_500 = df.index.get_level_values('heightAboveGround') == 500.0

    bP15 = (x_condition) & (y_condition) & (height_condition_15)
    bP150 = (x_condition) & (y_condition) & (height_condition_150)
    bP250 = (x_condition) & (y_condition) & (height_condition_250)
    bP500 = (x_condition) & (y_condition) & (height_condition_500)

    return bP15, bP150, bP250, bP500

def bridgeElevation(point: tuple[float], points: list[tuple[float]], point_values: list[tuple[float]]) -> float:
    """
    Args:
        point (tuple[float]): the point to be looked at in isn93
        w (Window): a window of a dataset containing the elevation of points surrounding a given point
    Returns:
        A single value representing the elevation at given point
    """
    try:
        distances = getDistances(point, points)
        T, d = sum(distances), len(points)
        weights = getWeights(distances, T, d-1)

        assert round(sum(weights),6) == 1, "The weights didn't sum up to 1"

        res = sum([weights[i] * point_values[i] for i in range(d)])

        return res
    except Exception as e:
        print(f"Unable to bridge elevation with exception {e}")

# Find all 8 relevant Carrapoints for a given point by vedurstofa
# i.e. the four points closest to given point for two closest times in Carra (because Carra is on 3 hour interval)
# b is before and a is after
def bridgeCarra(vPoint, bGrid, aGrid):
    x, y, time, f, fg, d = vPoint
    bCarraPoints, aCarraPoints = getCarraPointsToBridge(x, y, bGrid), getCarraPointsToBridge(x, y, aGrid)
    return bCarraPoints, aCarraPoints

# Find the Carra points to bridge, that is given a quadtree of the Carra points and the point of interest
# from Vedurstofa, return the four Carra points that bound the given point
def getCarraPointsToBridge(x, y, gridIndex, grid_dist = 2500):
    bbox = (x-grid_dist, y-grid_dist, x+grid_dist, y+grid_dist)
    points = gridIndex.intersect(bbox)
    return points

# Bridge the Carra points within space, that is given x,y coordinates of a weather station and the four closest points to
# That point in the Carra grid, bridge spatially
def bridgeSpatialCarra(X, Y, points, features_to_bridge):
    interp_features = [bridgeSpatialCarraFeature(X, Y, points, feature).item(0) for feature in features_to_bridge]
    #for feature in features_to_bridge:
    #    interp = bridgeSpatialCarraFeature(X, Y, points, feature)
    #    interp_features.append(interp.item(0))
    return interp_features

# Bridge a specific feature (band) of the carra points
def bridgeSpatialCarraFeature(X, Y, points, feature):
    coord_points = points[['X', 'Y']].values #np.array([(point['X'], point['Y']) for index, point in points.iterrows()])
    feature_value =  points[feature] #np.array(points[feature])

    distances = np.sqrt(np.sum((coord_points - (X, Y))**2, axis = 1))
    distances[distances == 0] = 1e-10
    distances **= -1
    distances /= np.sum(distances)
    interpolated_value = np.average(feature_value, weights=distances) # np.dot(weights, feature)

    return interpolated_value

# Given the bridged points before and after, that is at the given coordinates on the before and after 3 hour interval
# then this function will bridge between these two time points given how close they are to the actual time
def bridgeCarraTemporal(time, bPoint, aPoint):
    time_b, wdir_b, t_b, ws_b, pres_b = bPoint
    time_a, wdir_a, t_a, ws_a, pres_a = aPoint
    time_b, time_a = getTimeDifference(time, time_b, time_a)
    prop_b, prop_a = getProportions(time_b, time_a)
    return [weightInterp(wdir_b, wdir_a, prop_b, prop_a), weightInterp(t_b, t_a, prop_b, prop_a), 
            weightInterp(ws_b, ws_a, prop_b, prop_a), weightInterp(pres_b, pres_a, prop_b, prop_a)]

def weightInterp(fa, fb, wa, wb):
    return fa * wa + fb * wb
    
# Get datetime object from string time
def parseTime(time_str):
    return datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')

# Get the difference in time for both the earlier and later time for the given time
def getTimeDifference(given_time_str, time1, time2): #time_str1, time_str2):
    #time1, time2 = parseTime(time_str1), parseTime(time_str2)
    given_time = parseTime(given_time_str)
    
    time_b = given_time - time1
    time_a = time2 - given_time

    return time_b, time_a

# Get the constants that represent the linear weight given to the point before and the point after
def getProportions(time_b, time_a):
    total_seconds = 180*60

    prop_b, prop_a = time_a.seconds / total_seconds, time_b.seconds / total_seconds

    return prop_b, prop_a