import pandas as pd, numpy as np, os
from utils.util import is_laptop, flattenList
from sklearn.preprocessing import MinMaxScaler


def get_data_path():
    path = 'E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/Combined/' if not is_laptop() else None
    files = os.listdir(path)
    files = [f for f in files if os.path.isfile(os.path.join(path, f))]
    files.sort(key = lambda x: os.path.getmtime(os.path.join(path, x)), reverse=True)


    print(files[0])

    if files:
        return path + files[0]
    else:
        return None
    
def get_normalized_data():
    df = pd.read_feather(get_data_path())
    df = df.reset_index()
    n_elevation_points = df.elevation.iloc[0].shape[0]
    elevation_columns = pd.DataFrame(df['elevation'].tolist(), columns=[f'e{i}' for i in range(n_elevation_points)])
    df = pd.concat([df, elevation_columns], axis=1)
    df = df.drop(['index'], axis = 1)
    return normalize_data(df)

def normalize_data(df: pd.DataFrame):
    scaler = MinMaxScaler()
    df = df[~df.isin([np.inf, -np.inf]).any(axis=1)]
    df = df.drop(['landscape_points', 'elevation', 'stod'], axis = 1)
    df = df.dropna()
    numerical_columns = df.columns[df.columns != 'time']
    normalized_data = scaler.fit_transform(df[numerical_columns])
    normalized_df = pd.DataFrame(normalized_data, columns = numerical_columns)
    return normalized_df

df = pd.read_feather('E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/Combined/merged_measured_reanalysis_landscape_2sectors_25ms_24hr_25_3_24.feather')

print(df[['f', 'fg']])