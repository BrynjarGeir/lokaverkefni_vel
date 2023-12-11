from pyarrow import feather
import pandas as pd
import pickle

def updateStationToLatLon(dictFilePath: str = "/mnt/d/Skóli/lokaverkefni_vel/data/Vedurstofa/isn93StationCoordinates.pkl",
                              strippedFilePath: str = "/mnt/d/Skóli/lokaverkefni_vel/data/Vedurstofa/stripped_10min.feather") -> None:
    
    with open(dictFilePath, 'rb') as f:
        conversionDict = pickle.load(f)

    #print(conversionDict.keys())
    print(conversionDict[1350])

    df = pd.read_feather(strippedFilePath)
    df['lat'] = df['lon'] = None

    for index, row in df.iterrows():
        lat, lon = conversionDict[int(row['stod'])]['lat'], conversionDict[int(row['stod'])]['lon']
        df.at[index, 'lat'] = lat
        df.at[index, 'lon'] = lon

    df.to_feather(strippedFilePath)

updateStationToLatLon()
    