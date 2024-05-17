import pandas as pd, numpy as np, dill as pickle, os
from utils.util import getTopLevelPath
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from math import cos, pi

# Rounds to next hour so as to be able to directly compare with the vedur klst file
def next_hour(timi):
    return timi.ceil('h')

def transformedWindDirection(row):
    X, Y, d0 = row.X, row.Y, 270 - row.d
    inlandX, inlandY = 520000, 485000

    c = np.arctan2(Y - inlandY, X - inlandX) * 180/ pi

    # Wind direction relative to the direction from the center of Iceland to station
    # Wind directly from the ocean gives twd = 180
    twd = abs(d0 - c)

    if twd > 180:
        twd =  360 - twd
    
    return cos(twd * pi / 180)

def custom_distribution_transform(x, threshold = 20):
    max_decay = 1.2
    max_growth = 6
    decay = lambda z : 1 + (max_decay-1) * np.exp(threshold - z)
    growth = lambda z : 1 + (max_growth - 1) * np.exp(z - threshold)
    amplification_factors = np.where(x <= threshold, growth(x) , decay(x))
    y = amplification_factors * x + 8
    return y

def get_data_path():
    folder_path = getTopLevelPath() + 'data/Model/'
    file_path = folder_path + max([file for file in os.listdir(folder_path) if file.endswith('.feather')], key = lambda f: os.path.getmtime(folder_path + f))
    return file_path

# Get data for plotting and such
def get_data():
    data_path = get_data_path()
    df = pd.read_feather(data_path)
    df = df.reset_index()
    df['twd'] = df.apply(transformedWindDirection, axis = 1)
    df = df[df.f < df.fg]
    df['gust_factor'] = df.fg / df.f
    df_unfolded = df.elevations.apply(pd.Series)
    df = pd.concat([df, df_unfolded], axis = 1)
    df = df.drop(['index'], axis = 1)
    return df

def get_stats(WithAWSL = False):
    folder = getTopLevelPath() + 'data/Measured/Stats/'
    if WithAWSL:
        folder += 'WithAWSL/'
    with open(folder + 'windspeeds_stats.pkl', 'rb') as f:
        windspeeds = pickle.load(f)
    with open(folder + 'gustspeeds_stats.pkl', 'rb') as f:
        gustpeeds = pickle.load(f)
    with open(folder + 'winddirections_stats.pkl', 'rb') as f:
        winddirections = pickle.load(f)
    with open(folder + 'gust_factor_stats.pkl', 'rb') as f:
        gustfactor = pickle.load(f)
    with open(folder + 'years_stats.pkl', 'rb') as f:
        years = pickle.load(f)
    with open(folder + 'months_stats.pkl', 'rb') as f:
        months = pickle.load(f)
    return windspeeds, gustpeeds, winddirections, gustfactor, years, months


# Get data for training and such    
def get_normalized_data():
    scaler = StandardScaler()
    df = pd.read_feather(get_data_path())
    df = df.reset_index()
    df = df.drop(['index'], axis = 1)
    df['twd'] = df.apply(transformedWindDirection, axis = 1)
    df = df[df.f < df.fg]
    df['gust_factor'] = df.fg / df.f
    df_unfolded = df.elevations.apply(pd.Series)
    df = pd.concat([df, df_unfolded], axis = 1)
    n_components = df_unfolded.shape[1]
    df.iloc[:, -n_components:] = df.iloc[:, -n_components:].sub(df.station_elevation, axis = 0)

    df = df.drop(['elevations', 'N_01', 'N_12', 'N_02', 'XYd'], axis = 1)
    df = df.replace([-np.inf, np.inf], np.nan)
    df = df.dropna()
    df.columns = df.columns.astype(str)

    y = df.gust_factor
    X = df[['t_15', 'ws_15', 'wd_15', 't_250', 'ws_250', 'wd_250', 't_500', 'ws_500', 'wd_500', 'Ri_02', 'N_02_squared', 'station_elevation', 'twd'] + [str(i) for i in range(n_components)]]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size = 0.2, random_state = 42)
    X_train, X_val, X_test  = scaler.fit_transform(X_train), scaler.fit_transform(X_val), scaler.fit_transform(X_test)
    
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)

# Just testing using the transformed reanalysis data. The reanalysis data is shifted to the left of the measured data
# Because it represents some sort of three hour average and the measured only a 10 minute average
def get_normalized_transformed_data():
    scaler = StandardScaler()
    df = pd.read_feather(get_data_path())
    df = df.reset_index()
    df = df.drop(['index'], axis = 1)
    df['twd'] = df.apply(transformedWindDirection, axis = 1)
    df = df[df.f < df.fg]
    df['gust_factor'] = df.fg / df.f
    df_unfolded = df.elevations.apply(pd.Series)
    df = pd.concat([df, df_unfolded], axis = 1)
    n_components = df_unfolded.shape[1]
    df.iloc[:, -n_components:] = df.iloc[:, -n_components:].sub(df.station_elevation, axis = 0)

    df.ws_15, df.ws_150, df.ws_250, df.ws_500 = custom_distribution_transform(df.ws_15), custom_distribution_transform(df.ws_150), custom_distribution_transform(df.ws_250), custom_distribution_transform(df.ws_500)

    df = df.drop(['landscape_points', 'elevations', 'N_01', 'N_12', 'N_02'], axis = 1)
    df = df.replace([-np.inf, np.inf], np.nan)
    df = df.dropna()
    df.columns = df.columns.astype(str)

    y = df.gust_factor
    X = df[['t_15', 'ws_15', 'wd_15', 't_250', 'ws_250', 'wd_250', 't_500', 'ws_500', 'wd_500', 'Ri_02', 'N_02_squared', 'station_elevation', 'twd'] + [str(i) for i in range(n_components)]]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size = 0.2, random_state = 42)
    X_train, X_val, X_test  = scaler.fit_transform(X_train), scaler.fit_transform(X_val), scaler.fit_transform(X_test)
    
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)