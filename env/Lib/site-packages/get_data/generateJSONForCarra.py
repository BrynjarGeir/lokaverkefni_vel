import pandas as pd, dill as pickle, json
from tqdm import tqdm
from utils.transform import transformISN93ToWGS84
from time import time

with open('D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stationsLonLatXY.pkl', 'rb') as f:
    stationsLonLatXY = pickle.load(f)

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

def getXY(stod):
    return stationsLonLatXY[stod][2:]

def generateListOfDatetimesCoordinates(vedurPath: str = 'D:/Skóli/lokaverkefni_vel/data/Vedurstofa/combined_10min_20ms_25_3_24_24hr.feather') -> list:
    vedurDF = pd.read_feather(vedurPath)

    vedurDF['X'], vedurDF['Y'] = zip(*vedurDF['stod'].map(getXY))

    vedurDF = vedurDF.dropna(subset = ['timi', 'f', 'fg', 'stod', 'd', 'X', 'Y'])
    vedurDF['pointsYX'] = list(zip(vedurDF.Y, vedurDF.X))

    grouped_df = vedurDF.groupby('timi').agg({'pointsYX': list}).reset_index()
    grouped_df.timi = pd.to_datetime(grouped_df.timi)
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

    with open('D:/Skóli/lokaverkefni_vel/data/carra24klst-20ms-25-3-24.json', 'w') as f:
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