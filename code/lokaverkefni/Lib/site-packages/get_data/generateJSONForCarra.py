import pandas as pd, dill as pickle, json, numpy as np
from tqdm import tqdm
from utils.elevation import findLandscapeDistribution
from utils.transform import transformISN93ToWGS84
from datetime import datetime
from time import time
def getDTXYD(row):
    return row.timi, row.X, row.Y, row.d

def getLonLatFromXY(pointsXY):
    X, Y = [p[0] for p in pointsXY], [p[1] for p in pointsXY]

    lon, lat = transformISN93ToWGS84(X, Y)

    return lon, lat

def generateJSON(coordinates: list, datetime: str) -> str:
    coordinates = [arr.tolist() for arr in coordinates]
    res = {
            datetime:
                coordinates
    }
    return res

def generateListOfDatetimesCoordinates(vedurPath: str = "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/Stripped_25ms_12klst_10min.feather") -> list:
    vedurDF = pd.read_feather(vedurPath)
    vedurDF = vedurDF.dropna(subset = ['timi', 'f', 'fg', 'stod', 'd', 'X', 'Y'])
    vedurDF['pointsXY'] = vedurDF.apply(lambda row: findLandscapeDistribution((row.X, row.Y), row.d, n = 10, k = 5, angleRange=[0]), axis = 1)
    vedurDF.pointsXY = vedurDF.pointsXY.apply(lambda points: [points[0][0]] + [p[0] for p in points])

    grouped_df = vedurDF.groupby('timi').agg({'pointsXY': list}).reset_index()
    grouped_df['flattened'] = grouped_df.pointsXY.apply(lambda x: [arr for sublist in x for arr in sublist])

    grouped_df.timi = grouped_df.timi.dt.strftime('%Y-%m-%dT%H:%M:%S')
    
    return grouped_df

def generateAllJSON():
    grouped_df = generateListOfDatetimesCoordinates()

    grouped_df['JSON'] = grouped_df.apply(lambda row: generateJSON(row.flattened, row.timi), axis = 1)

    coords_dict = {key: value for d in grouped_df.JSON for key,value in d.items()}

    final_dict = {"param": {"product_type": "analysis", 
                            "variable": ["Wind speed", "Wind direction", "Pressure", "Temperature"], 
                            "height_levels":[15, 150, 250, 500]},
                "timestamp_location": coords_dict}

    res = json.dumps(final_dict, indent = 4)

    with open('D:/Skóli/lokaverkefni_vel/data/carraJSON12klst.json', 'w') as f:
        json.dump(res, f)

def convertPKLToJSON():
    with open('D:/Skóli/lokaverkefni_vel/data/carraJSON24.pkl', 'rb') as f:
        lst = pickle.load(f)
    with open('D:/Skóli/lokaverkefni_vel/data/carraJSON24.json', 'w') as f:
        json.dump(lst, f, indent = 4)

start = time()
generateAllJSON()
end = time()

print(f"Generating all the JSON and such took {end - start} seconds")