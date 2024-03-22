import pandas as pd, os, dill as pickle, csv
from tqdm import tqdm
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

def tooClose(dt1, dt2, threshold):
    return abs((dt1 - dt2)) < pd.Timedelta(threshold, 's')

def combineVedurstofaVg10minTXTfiles(path_10min: str = 'E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/Vedurstofa/10min/', outputpath: str = 'E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/Vedurstofa/combined_10min.feather') -> None:
    files = [os.path.join(path_10min, file) for file in os.listdir(path_10min)]
    columns, df = None, None

    for file in tqdm(files, total = len(files)):
        with open(file, 'r') as f:
            reader = list(csv.reader(f))
            
        if not columns:
            columns = reader[0]
        
        lines = reader[1:]

        if df is None:
            df = pd.DataFrame(lines, columns = columns)
        else:
            df = pd.concat([df, pd.DataFrame(lines, columns = columns)])
        
        df.f = pd.to_numeric(df.f, errors = 'coerce')
        df = df[df.f >= 20]

    df.timi = pd.to_datetime(df.timi)
    df.stod = df.stod.astype(int)
    df.f = pd.to_numeric(df.f, errors = 'coerce')
    df.fg = pd.to_numeric(df.fg, errors = 'coerce')
    df.fsdev = pd.to_numeric(df.fsdev, errors = 'coerce')
    df.d = pd.to_numeric(df.d, errors = 'coerce')
    df.dsdev = pd.to_numeric(df.dsdev, errors = 'coerce')

    df.to_feather(outputpath)

def filterWithThreshold(vedurPath: str = 'E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/Vedurstofa/combined_10min_20ms.feather', outputpath: str = 'E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/Vedurstofa/combined_10min_20ms_24hr.feather', threshold: str = '1 day'):
    vedur_df = pd.read_feather(vedurPath)
    filtered_data, columns, stations = [], vedur_df.columns, vedur_df.stod.unique()

    print(f'The shape of the unfiltered dataframe is {vedur_df.shape}')

    for station in tqdm(stations, total = len(stations)):
        subset_df = vedur_df[station == vedur_df.stod]
        subset_df = subset_df.reset_index(drop = True)

        while not subset_df.empty:
            idx = subset_df.f.idxmax()
            time_of_max = subset_df.iloc[idx].timi

            filtered_data.append(subset_df.iloc[idx])

            subset_df = subset_df[abs(subset_df.timi - time_of_max) >= pd.Timedelta('1 day')]

            subset_df = subset_df.reset_index(drop = True)

    filtered_df = pd.DataFrame(filtered_data, columns=columns)

    filtered_df = filtered_df.sort_values(by=['stod', 'timi'])

    filtered_df = filtered_df.reset_index(drop=True)

    print(f'The shape of the filtered dataframe is {filtered_df.shape}')

    filtered_df.to_feather(outputpath)
                
