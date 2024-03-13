import pandas as pd, dill as pickle, json, numpy as np
from tqdm import tqdm
from utils.elevation import findLandscapeDistribution
from utils.transform import transformISN93ToWGS84
from datetime import datetime, timedelta
from time import time
def getDTXYD(row):
    return row.timi, row.X, row.Y, row.d

def getLonLatFromXY(pointsXY):
    X, Y = [p[0] for p in pointsXY], [p[1] for p in pointsXY]

    lon, lat = transformISN93ToWGS84(X, Y)

    return lon, lat

def generateJSON(coordinates: list, datetime: str) -> str:
    #coordinates = [arr.tolist() for arr in coordinates]
    res = {
            datetime:
                coordinates
    }
    return res

def generateListOfDatetimesCoordinates(vedurPath: str = "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/Stripped_20ms_24klst_10min-dropped_too_close.feather") -> list:
    vedurDF = pd.read_feather(vedurPath)
    vedurDF = vedurDF.dropna(subset = ['timi', 'f', 'fg', 'stod', 'd', 'X', 'Y'])
    #vedurDF['pointsYX'] = vedurDF.apply(lambda row: findLandscapeDistribution((row.X, row.Y), row.d, n = 10, k = 1, angleRange=[0]), axis = 1) # k = 5?6
    vedurDF['pointsYX'] = list(zip(vedurDF.Y, vedurDF.X))
    #vedurDF.pointsYX = vedurDF.pointsXY.apply(lambda points: [p[0] for p in points])

    grouped_df = vedurDF.groupby('timi').agg({'pointsYX': list}).reset_index()

    grouped_df.timi = pd.to_datetime(grouped_df.timi)
    
    #grouped_df['flattened'] = grouped_df.pointsYX.apply(lambda x: [arr for sublist in x for arr in sublist])

    #start_date = (min(grouped_df.timi) + timedelta(days=365)).replace(day = 1, hour = 0, minute = 0, second = 0, microsecond = 0)
    #start_date = start_date.replace(year = 2019, month = 1, day = 1, hour = 0, minute = 0, second = 0, microsecond = 0)
    #end_date = start_date.replace(year = 2019, month = 1, day = 31, hour = 23, minute = 59, second = 59, microsecond = 59)
    #grouped_df = grouped_df[(grouped_df.timi >= start_date) & (grouped_df.timi <= end_date)]

    grouped_df.timi = grouped_df.timi.dt.strftime('%Y-%m-%dT%H:%M:%S')

    return grouped_df

def generateAllJSON():
    grouped_df = generateListOfDatetimesCoordinates()

    grouped_df['JSON'] = grouped_df.apply(lambda row: generateJSON(row.pointsYX, row.timi), axis = 1) #flattened

    coords_dict = {key: value for d in grouped_df.JSON for key,value in d.items()}

    res = {"param": {"product_type": "analysis", 
                            "variable": ["Wind speed", "Wind direction", "Pressure", "Temperature"], 
                            "height_levels":[15, 150, 250, 500],
                            "feather_file": "interpolatedCarra.feather"},
                "timestamp_location": coords_dict}

    with open('D:/Skóli/lokaverkefni_vel/data/carra24klst-20ms-13-3-24-dropped-too-close.json', 'w') as f:
        json.dump(res, f, indent = 4)

def convertPKLToJSON():
    with open('D:/Skóli/lokaverkefni_vel/data/carraJSON24.pkl', 'rb') as f:
        lst = pickle.load(f)
    with open('D:/Skóli/lokaverkefni_vel/data/carraJSON24.json', 'w') as f:
        json.dump(lst, f, indent = 4)

start = time()
generateAllJSON()
end = time()

print(f"Generating all the JSON and such took {end - start} seconds")
        
#df = pd.read_feather("D:/Skóli/lokaverkefni_vel/data/Vedurstofa/Stripped_25ms_24klst_10min.feather")
#df_duplicated = df.loc[df.duplicated(subset='timi')]

#print(df_duplicated)