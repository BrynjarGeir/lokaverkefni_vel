#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pandas as pd, dill as pickle, os
from utils.calculateConstants import *
from utils.util import getTopLevelPath
from utils.elevation import getStationElevations, getStationElevationCircles
from datetime import date
from tqdm.notebook import tqdm

import pandas as pd, os


# In[3]:


folder_path =  getTopLevelPath() + 'data/'
stationsLonLatXY_path = folder_path + 'Measured/stationsLonLatXY.pkl'
measured_path = folder_path + 'Measured/Processed/' + max(os.listdir(folder_path + 'Measured/Processed/'), key = lambda f: os.path.getmtime(folder_path + 'Measured/Processed/' + f))
reanalysis_path = folder_path + 'Reanalysis/' + max([file for file in os.listdir(folder_path + 'Reanalysis/') if file.endswith('.feather')], key = lambda f: os.path.getmtime(folder_path + 'Reanalysis/' + f))
elevation_path = folder_path + "Elevation/IslandsDEMv1.0_20x20m_isn93_zmasl.tif"

se = getStationElevations()
ec = getStationElevationCircles()

today = date.today().strftime("%Y-%m-%d")
outputpath = folder_path + f'Model/data_{today}.feather'
outputpath_for_errors = folder_path + f'Model/Errors/error_{today}.feather'


# In[3]:


def addLonLatXYtoMeasured(df, stationsLonLatXY_path = stationsLonLatXY_path):
    with open(stationsLonLatXY_path, 'rb') as f:
        stationsLonLatXY = pickle.load(f)
    def get_lon_lat_X_Y(stod):
        return stationsLonLatXY.get(stod, (np.nan, np.nan, np.nan, np.nan))

    lon, lat, X, Y = zip(*df.stod.map(get_lon_lat_X_Y))
    df['lon'], df['lat'], df['X'], df['Y'] = lon, lat, X, Y
    return df


# In[4]:


def addElevationCircles(stod):
    return ec[stod]


# In[5]:


def addStationElevations(stod):
    return se[stod]


# In[6]:


def addElevation(df):
    df['XYd'] = list(zip(df.X, df.Y, df.wd_15))
    tqdm.pandas(desc = 'Adding station elevations...')
    df['station_elevation'] = df.stod.progress_map(addStationElevations)
    tqdm.pandas(desc = 'Adding landscape elevation...')
    ec = getStationElevationCircles()
    df['elevations']  = df.stod.progress_map(addElevationCircles)

    return df


# In[7]:


def prepareMeasurements(df, stationsLonLatXY_path, decimal_places = 4):
    df = df.drop(['fsdev', 'dsdev'], axis = 1)
    df = df.rename(columns = {'timi':'time'})
    df = addLonLatXYtoMeasured(df)
    df = df.round(decimal_places)
    return df


# In[8]:


def prepareRenalysis(df, decimal_places = 4):
    df = df.rename(columns = {'Wind speed':'ws', 'Wind direction': 'wd', 'Pressure':'p', 'Temperature':'t'})
    df = df.drop_duplicates(subset=['lon', 'lat', 'time', 'height_level'])
    df = df.pivot(index = ['lon', 'lat', 'time'], columns = 'height_level')
    df = df.drop(columns='yr_month')
    df.columns = [f'{col[0]}_{col[1]}' for col in df.columns]
    df = df.reset_index()
    df.time = pd.to_datetime(df.time)
    df = df.round(decimal_places)
    df[['Ri_01', 'Ri_12', 'Ri_02']] = df.apply(rowRichardson, axis = 1).to_list()
    df[['N_01', 'N_12', 'N_02']] = df.apply(rowBruntVaisala, axis = 1).to_list()
    df[['N_01_squared', 'N_12_squared', 'N_02_squared']] = df.apply(rowBruntVaisalaSquared, axis = 1).to_list()
    df[['N_01', 'N_12', 'N_02']] = df[['N_01', 'N_12', 'N_02']].map(lambda x: (x.real, x.imag))
    return df


# In[9]:


def merge(measured_path = measured_path, reanalysis_path = reanalysis_path):
    measured_df = pd.read_feather(measured_path)
    reanalysis_df = pd.read_feather(reanalysis_path)
    measured_df = prepareMeasurements(measured_df, stationsLonLatXY_path)
    reanalysis_df = prepareRenalysis(reanalysis_df)
    merged_df = pd.merge(measured_df, reanalysis_df, on = ['time', 'lon', 'lat'], how = 'inner')
    merged_df = addElevation(merged_df)
    errors = merged_df[merged_df.fg <= merged_df.f]
    merged_df = merged_df[merged_df.fg > merged_df.f]

    merged_df.to_feather(outputpath)
    errors.to_feather(outputpath_for_errors)

