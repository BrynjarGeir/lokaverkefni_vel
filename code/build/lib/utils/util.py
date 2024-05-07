from math import dist
from datetime import date
import os, numpy as np

def getDistances(point, points) -> list[float]:
    return [dist(point, p) for p in points]

def getWeights(distances, T, d) -> list[float]:
    res = [(1-di/T) / d for di in distances]
    return res

def flattenList(lst: list[list]) -> list:
    flatten_list = []
    for row in lst:
        flatten_list.extend(row)
    return flatten_list

# Rounds to next hour so as to be able to directly compare with the vedur klst file
def next_hour(timi):
    return timi.ceil('h')

def is_laptop():
    return not 'Brynjar Geir' == os.getlogin()

def getTopLevelPath():
    folder_path = 'C:/Users/brynj/Documents/Mastersverkefni/lokaverkefni_vel/' if is_laptop() else 'C:/Users/Brynjar Geir/Documents/Mastersverkefni/lokaverkefni_vel/'
    return folder_path

def getToday():
    return date.today().strftime('%Y-%m-%d')

def safe_float_conversion(string):
    try:
        return float(string)
    except ValueError:
        return np.nan
    
def safe_int_conversion(string):
    try:
        return int(string)
    except ValueError:
        return np.nan