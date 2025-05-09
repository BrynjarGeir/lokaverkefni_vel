import pandas as pd, numpy as np, dill as pickle, os
from utils.util import getTopLevelPath
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from math import cos, pi
from tqdm.notebook import tqdm

# Rounds to next hour so as to be able to directly compare with the vedur klst file
def next_hour(timi):
    return timi.ceil('h')

def transformedWindDirection(cc):
    X, Y, d0 = cc
    d0 = 270 - d0
    inlandX, inlandY = 520000, 485000
    c = np.arctan2(Y - inlandY, X - inlandX) * 180/ pi
    # Wind direction relative to the direction from the center of Iceland to station
    # Wind directly from the ocean gives twd = 180
    twd = abs(d0 - c)
    if twd > 180:
        twd =  360 - twd
    return cos(twd * pi / 180)

def unfoldElevations(df):
    elevations_array = np.array(df.elevations.tolist())
    elevation_columns = pd.DataFrame(elevations_array, index=df.index)
    elevation_columns.columns = [f'elevation_{i}' for i in range(elevations_array.shape[1])]
    df = df.drop(['elevations'], axis = 1)
    df = pd.concat([df, elevation_columns], axis=1)

    return df

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

def get_data_chunks():
    chunks_path = getTopLevelPath() + 'data/Model/chunks/'
    chunk_files = [chunks_path + chunk for chunk in os.listdir(chunks_path) if chunk.endswith('.feather')]
    df = pd.DataFrame()
    for file in tqdm(chunk_files, total = len(chunk_files), desc = 'Looping through chunks...'):
        c_df = pd.read_feather(file)
        c_df = c_df[c_df.f >= 10]
        c_df['gust_factor'] = c_df.fg / c_df.f
        c_df = c_df[['gust_factor', 'ws_15', 'wd_15', 't_15', 'p_15', 'Ri', 'N_squared', 'station_elevation', 'X', 'Y', 'elevations']]
        s = np.isinf(c_df.N_squared).sum() + c_df.N_squared.isna().sum()
        df = pd.concat([df, c_df])
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

def get_normalized_data_chunks():
    df = get_data_chunks()
    df = df[df.gust_factor >= 1]
    print("Already filtered by gust factor being less than 1")
    df = df.reset_index()
    df = df.drop(['index'], axis = 1)
    tqdm.pandas(desc = 'Adding transformed wind direction...')
    df['cc'] = list(zip(df.X, df.Y, df.wd_15))
    df['twd'] = df.cc.progress_map(transformedWindDirection)
    df = df.drop(['cc', 'X', 'Y'], axis = 1)
    print("Finished adding transformed wind direction")
    pre_len = len(df.columns)
    df = unfoldElevations(df)
    n_components = len(df.columns) - pre_len
    df.iloc[:, -n_components:] = df.iloc[:, -n_components:].sub(df.station_elevation, axis = 0)
    print("Subtracted station elevation from landscape elevation")
    df = df.replace([-np.inf, np.inf], np.nan)
    df = df.dropna()
    df.columns = df.columns.astype(str)
    #print("About to write df to feather...")
    #df = df.reset_index()
    #df.to_feather("./model_data.feather")
    #print("Finished writing df to feather...")
    print("Ready to split")
    y = df.gust_factor
    X = df.drop(['gust_factor'], axis = 1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size = 0.2, random_state = 42)

    scaler = StandardScaler()
    X_train, X_val, X_test  = scaler.fit_transform(X_train), scaler.fit_transform(X_val), scaler.fit_transform(X_test)
    print("Train, val, test is ready")

    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


print(get_normalized_data_chunks())