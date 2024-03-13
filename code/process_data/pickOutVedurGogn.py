import pandas as pd
import os
from tqdm import tqdm
import dill as pickle
from utils.transform import getVedurLonLatInISN93


# Still needs to be implemented: adding clause to check when the 10 min max over hour doesn't match the hour max (probably 0)
def createStationsLonLatXY(stodTxtPath: str = 'D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stod.txt', outputPath: str = 'D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stationsLonLatXY.pkl', encoding: str = 'ISO-8859-1'):
    stationsDict = {}
    with open(stodTxtPath, 'r', encoding = encoding) as f:
        stations = [a.strip().split(',') for a in f.readlines()][1:]
        stations = [[int(a[0]), a[1], float(a[2]), float(a[3]), float(a[4]) if a[4].isnumeric() else a[4], a[5]] for a in stations]
    for station in stations:
        latitude, longitude = station[2], station[3]
        x, y = getVedurLonLatInISN93(longitude, latitude)
        stationsDict[station[0]] = (-longitude, latitude, x, y)

    with open(outputPath, 'wb') as f:
        pickle.dump(stationsDict, f)

# Given a minimum for a given column (like wind speed or gust) select only the lines that adhere to that
# and write to feather file for a given station
def selectFromStation(filepath, wFilePath, band = 2, limit = 25):
    with open(filepath, 'r') as f:
        res = [line.strip().split(',') for line in f.readlines()]
        header = res[0]
        res = [[a[i] if i == 0 else int(a[i]) if i == 1 else float(a[i]) for i in range(7)] for a in res[1:]]
        res = [a for a in res if a[band] >= limit]

# Given a directory with the station files and an output directory select the lines that match for every station and create
# Feather files
def stripData(directory: str, outputPath: str, limit: float = 25, band: int = 2):
    files = [file for file in os.listdir(directory) if file.startswith('f_10min') and file.endswith('.txt')]
    header = None
    ans = []
    with open('D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stationsLonLatXY.pkl', 'rb') as f:
        stationsLonLatXY = pickle.load(f)

    for filename in tqdm(files, total = len(files)):
        filepath = directory + filename
        lon, lat, x, y =  [None for _ in range(4)]
        try:
            with open(filepath, 'r') as f:
                res = [line.strip().split(',') for line in f.readlines()]
                if header == None: 
                    header = res[0] + ['longitude', 'latitude', 'X', 'Y']
                res = [
                    [a[0] if a[0] != '' else None, int(a[1]) if a[1] != '' else None] + [float(a[i]) if a[i] != '' else None for i in range(2,len(a))]
                    for a in res[1:]
                ]
                res = [a for a in res if a[band] >= limit]
                if len(res) == 0:
                    continue
                if not lon:
                    lon, lat, x, y = stationsLonLatXY[res[0][1]]
                res = [a + [lon, lat, x, y] for a in res]
                ans.extend(res)
        except Exception as e:
            print(f"Unable to add file {filename} with exception {e}")
    print(f"Total number of observations above {limit} m/s average is {len(ans)}")
    df = pd.DataFrame(ans, columns = header)
    print(df)
    df.to_feather(outputPath)
     
# Call stripData for all types of station data (10 min vedurstofa, klst vedurstofa and vegagerdin)
def stripAllData():
    commonPath = "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/"
    stripData(commonPath, '10min/', 'selected_10min/')
    stripData(commonPath, 'klst/', 'selected_klst/')
    stripData(commonPath, 'vg/', 'selected_vg/')

def tooClose(dt1, dt2, threshold):
    return abs((dt1 - dt2)) < pd.Timedelta(threshold, 's')

# Take the stripped by a limit dataframe and limit the information from it so that for a given weatherstation we won't have the same
# weather twice or more, that is I won't have any two observations that are within threshold seconds of each other
def stripToDifferentWeathers(vedurPath: str = 'D:/Skóli/lokaverkefni_vel/data/Vedurstofa/Stripped_25ms_10min.feather', threshold: int = 60*60*24):
    vedurDF = pd.read_feather(vedurPath)
    vedurDF.timi = pd.to_datetime(vedurDF.timi)
    vedurDF = vedurDF.sort_values(by=['stod', 'timi', 'f'])
    n = len(vedurDF)

    vedurDF = iterativeFilteredDF(vedurDF, threshold)
    vedurDF.timi = pd.to_datetime(vedurDF.timi)

    print(f"The length of the dataframe is now {len(vedurDF)} but used to be {n}. This is a shrinking to {len(vedurDF) / n * 100}% of original size.")
    vedurDF.to_feather('D:/Skóli/lokaverkefni_vel/data/Vedurstofa/Stripped_25ms_24klst_10min.feather')

def iterativeFilteredDF(vedurDF, threshold):
    filteredDF, prev_row = pd.DataFrame(columns = vedurDF.columns), None

    for index, row in tqdm(vedurDF.iterrows(), total = len(vedurDF)):
        if prev_row is not None and prev_row.stod == row.stod and tooClose(prev_row.timi, row.timi, threshold):
            if prev_row.f < row.f:
                filteredDF.loc[len(filteredDF) - 1] = row
        else:
            filteredDF.loc[len(filteredDF)] = row
        prev_row = row

    return filteredDF

