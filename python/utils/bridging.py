from scipy.interpolate import griddata
from datetime import datetime
from rasterio.windows import Window
import numpy as np, pandas as pd
from utils.util import getDistances, getWeights, flattenList

def findBoundingPoints(point: tuple[float], df: pd.DataFrame, gridSpacing: float = 2500) -> list:
    """
    Args:
        df (DataFrame): a dataframe that contains all the griddata from Carra files
        gridSpacing (float): the distance between numbers in the Carra grid (2500 m)
        point (tuple(float)): the given point from Vedur data
    Returns:
        A index list of group of points (4, except given point matches grid point (unlikely)) that bound the given vedur
        data point. That is the indices of the four relevant points.
    """
    target_lat, target_lon = point
    lat_condition = (df['latitude'].between(target_lat - gridSpacing, target_lat + gridSpacing))
    lon_condition = (df['longitude'].between(target_lon - gridSpacing, target_lon + gridSpacing))
    height_condition_15 = (df['heightAboveGround'] == 15.0)
    height_condition_150 = (df['heightAboveGround'] == 150.0)
    height_condition_250 = (df['heightAboveGround'] == 250.0)
    height_condition_500 = (df['heightAboveGround'] == 500.0)
    
    bP15 = lat_condition & lon_condition & height_condition_15
    bP150 = lat_condition & lon_condition & height_condition_150
    bP250 = lat_condition & lon_condition & height_condition_250
    bP500 = lat_condition & lon_condition & height_condition_500

    return bP15, bP150, bP250, bP500

def bridgeElevation(point: tuple[float], w: Window, coordinates: list[list[float]]) -> float:
    """
    Args:
        point (tuple[float]): the point to be looked at in isn93
        w (Window): a window of a dataset containing the elevation of points surrounding a given point
    Returns:
        A single value representing the elevation at given point
    """
    try:
        w_flattened = flattenList(w)
        distances = getDistances(point, coordinates)
        T, d = sum(distances), len(w_flattened)
        weights = getWeights(distances, T, d-1)


        assert(round(sum(weights),6) == 1)

        res = sum([weights[i] * w_flattened[i] for i in range(d)])

        return res
    except Exception as e:
        print(f"Unable to bridge elevation with exception {e} and the length of the w was {len(w)}")
        print(w)

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
def bridgeSpatialCarra(x, y, points, features_to_bridge):
    interp_features = []
    for feature in features_to_bridge:
        interp = bridgeSpatialCarraFeature(x, y, points, feature)
        interp_features.append(interp.item(0))
    return interp_features

# Bridge a specific feature (band) of the carra points
def bridgeSpatialCarraFeature(x, y, points, feature):
    coord_points = np.array([(point['longitude'], point['latitude']) for index, point in points.iterrows()])
    feature =  np.array(points[feature])

    interp = griddata(coord_points, feature, (x,y), method = 'linear') # Athuga hvað þýðir - sjór/land

    return interp

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