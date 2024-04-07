import pandas as pd, numpy as np, os
from utils.util import is_laptop, flattenList
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from math import sqrt, sin, cos, acos, pi

from time import time


def get_data_path():
    folder_path = 'D:/Skoli/Mastersverkefni/lokaverkefni_vel/data/' if is_laptop() else 'E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/data/'
    file_path = folder_path + 'NailStripped_W_Elevation/' + max(os.listdir(folder_path + 'NailStripped_W_Elevation/'),
                key = lambda f: os.path.getmtime(folder_path + 'NailStripped_W_Elevation/' + f))
    return file_path

# Get data for plotting and such
def get_data():
    df = pd.read_feather(get_data_path())
    df = df.reset_index()
    df['relativeCorner'] = df.apply(cornerFromCenterLand, axis = 1)
    df = df[df.f < df.fg]
    df['gust_factor'] = df.fg / df.f
    df_unfolded = df.elevations.apply(pd.Series)
    df = pd.concat([df, df_unfolded], axis = 1)
    df = df.drop(['index'], axis = 1)

    return df

# Get data for training and such    
def get_normalized_data(n_components: int = 10):
    scaler = StandardScaler()
    df = pd.read_feather(get_data_path())
    df = df.reset_index()
    df = df.drop(['index'], axis = 1)

    df['relativeCorner'] = df.apply(cornerFromCenterLand, axis = 1)
    df[['N_01_real', 'N_01_imag']] = df['N_01'].apply(pd.Series)
    df[['N_12_real', 'N_12_imag']] = df['N_12'].apply(pd.Series)
    df[['N_02_real', 'N_02_imag']] = df['N_02'].apply(pd.Series)
    df = df[df.f < df.fg]
    df['gust_factor'] = df.fg / df.f
    df_unfolded = df.elevations.apply(pd.Series)
    df = pd.concat([df, df_unfolded], axis = 1)

    df = df.drop(['landscape_points', 'elevations', 'N_01', 'N_12', 'N_02'], axis = 1)

    df = applyPCA(df)

    df = df.replace([-np.inf, np.inf], np.nan)
    df = df.dropna()

    y = df.gust_factor
    X = df[['t_15', 'ws_15', 'Ri_02', 'N_02_real', 'N_02_imag', 'station_elevation', 'relativeCorner'] + ['PC' + str(i) for i in range(n_components)]]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size = 0.2, random_state = 42)
    X_train, X_val, X_test  = scaler.fit_transform(X_train), scaler.fit_transform(X_val), scaler.fit_transform(X_test)
    
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)

def applyPCA(df: pd.DataFrame, n_components: int = 10):
    n_elevations = df.columns[-1] + 1
    df.iloc[:, -n_elevations:] = df.iloc[:, -n_elevations:].sub(df.station_elevation, axis = 0)

    df_landscape_elevation = df.iloc[:, -n_elevations:]
    df_landscape_elevation = (df_landscape_elevation - df_landscape_elevation.mean()) / df_landscape_elevation.std()

    pca = PCA(n_components=n_components)
    compressed_features = pca.fit_transform(df_landscape_elevation)

    compressed_df = pd.DataFrame(data = compressed_features, columns = ['PC' + str(i) for i in range(n_components)])

    df = pd.concat([df, compressed_df], axis = 1)

    return df

def cornerFromCenterLand(row):
    X, Y, d = row.X, row.Y, row.d
    inlandX, inlandY = 520000, 485000

    len_v1 = sqrt((X-inlandX)**2 + (Y-inlandY)**2)

    v1 = ((X - inlandX)/len_v1, (Y - inlandY)/ len_v1)

    outX, outY = X + cos(d * pi / 180), Y + sin(d * pi / 180)

    len_v2 = sqrt(outX**2 + outY**2)

    v2 = (outX / len_v2, outY / len_v2)

    return acos(np.dot(v1, v2))