#!/usr/bin/env python
# coding: utf-8

from tensorflow.keras.regularizers import l2
from tensorflow.keras.callbacks import TensorBoard
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
#from keras_tuner import HyperParameters, Hyperband
from datetime import datetime

from math import cos, pi
from tqdm.notebook import tqdm

#from utils.model_eval import mean_absolute_percentage_error
#from utils.data import get_normalized_data_chunks

import pandas as pd, numpy as np, tensorflow as tf, os


def mean_absolute_percentage_error(y_true, y_pred):
    return tf.reduce_mean(tf.abs((y_true-y_pred) / y_true)) * 100.0

def get_data_chunks():
    chunks_path = '../data/Model/chunks/'
    chunk_files = [chunks_path + chunk for chunk in os.listdir(chunks_path) if chunk.endswith('.feather')]
    df = pd.DataFrame()
    for file in tqdm(chunk_files, total = len(chunk_files), desc = 'Looping through chunks...'):
        c_df = pd.read_feather(file)
        c_df = c_df[c_df.f >= 10]
        c_df['gust_factor'] = c_df.fg / c_df.f
        c_df = c_df[['gust_factor', 'ws_15', 'wd_15', 't_15', 'p_15', 'Ri', 'N_squared', 'station_elevation', 'X', 'Y']]
        s = np.isinf(c_df.N_squared).sum() + c_df.N_squared.isna().sum()
        df = pd.concat([df, c_df])
    return df

def transformedWindDirection(row):
    X, Y, d0 = row.X, row.Y, 270 - row.wd_15
    inlandX, inlandY = 520000, 485000

    c = np.arctan2(Y - inlandY, X - inlandX) * 180/ pi

    # Wind direction relative to the direction from the center of Iceland to station
    # Wind directly from the ocean gives twd = 180
    twd = abs(d0 - c)

    if twd > 180:
        twd =  360 - twd
    
    return cos(twd * pi / 180)

def get_normalized_data_chunks():
    scaler = StandardScaler()
    df = get_data_chunks()
    df = df.reset_index()
    df = df.drop(['index'], axis = 1)
    tqdm.pandas(desc = 'Adding transformed wind direction...')
    df['twd'] = df.progress_apply(transformedWindDirection, axis = 1)
    df = df[df.gust_factor >= 1]
    #df_unfolded = df.elevations.apply(pd.Series)
    #df = pd.concat([df, df_unfolded], axis = 1)
    #n_components = df_unfolded.shape[1]
    #df.iloc[:, -n_components:] = df.iloc[:, -n_components:].sub(df.station_elevation, axis = 0)
    df = df.replace([-np.inf, np.inf], np.nan)
    df = df.dropna()
    df.columns = df.columns.astype(str)

    y = df.gust_factor
    X = df.drop(['gust_factor', 'X', 'Y'], axis = 1)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 42)
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size = 0.2, random_state = 42)
    X_train, X_val, X_test  = scaler.fit_transform(X_train), scaler.fit_transform(X_val), scaler.fit_transform(X_test)
    
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)


today = datetime.today().strftime("%Y-%m-%d")
train, val, test = get_normalized_data_chunks()
X_train, y_train = train
X_val, y_val = val
X_test, y_test = test


def build_model(n_units = 64, activation = 'elu', penalty =  0.00168, n_layers = 11, optimizer = 'rmsprop'):
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Input(shape = (X_train.shape[1], )))
    model.add(tf.keras.layers.Dense(units = n_units, activation = activation, kernel_regularizer=l2(penalty)))
    model.add(tf.keras.layers.BatchNormalization())

    for _ in range(n_layers):
        model.add(tf.keras.layers.Dense(units = n_units, activation = activation, kernel_regularizer=l2(penalty)))
        model.add(tf.keras.layers.BatchNormalization())

    model.add(tf.keras.layers.Dense(units = n_units, activation = activation, kernel_regularizer=l2(penalty)))
    model.add(tf.keras.layers.Dropout(0.5))

    model.add(tf.keras.layers.Dense(units = 1, activation = 'linear'))

    model.compile(optimizer = optimizer, loss = mean_absolute_percentage_error)

    return model


model = build_model()
model.fit(X_train, y_train, epochs = 200, batch_size = 128, validation_data = (X_val, y_val))
results = model.evaluate(X_test, y_test, batch_size = 128)
print("test loss, test acc:", results)