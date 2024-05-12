#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd, dill as pickle, os
from utils.calculateConstants import *
from utils.util import getTopLevelPath
from utils.elevation import generateLandscapeDistribution2Sectors, generateElevationDistribution, findLandscapeElevation
from utils.transform import transformISN93ToWGS84
from datetime import date

import pandas as pd, rasterio, os


# In[2]:


folder_path =  getTopLevelPath() + 'data/'
stationsLonLatXY_path = folder_path + 'Measured/stationsLonLatXY.pkl'
measured_path = folder_path + 'Measured/Processed/' + max(os.listdir(folder_path + 'Measured/Processed/'), key = lambda f: os.path.getmtime(folder_path + 'Measured/Processed/' + f))
reanalysis_path = folder_path + 'Reanalysis/' + max([file for file in os.listdir(folder_path + 'Reanalysis/') if file.endswith('.feather')], key = lambda f: os.path.getmtime(folder_path + 'Reanalysis/' + f))
elevation_path = folder_path + "Elevation/IslandsDEMv1.0_20x20m_isn93_zmasl.tif"

today = date.today().strftime("%Y-%m-%d")
outputpath = folder_path + f'Model/data_{today}.feather'
outputpath_for_errors = folder_path + f'Model/Errors/error_{today}.feather'


# In[3]:


def addPointElevation(row, transform, index, elevation):
    X, Y = row.X, row.Y
    return findLandscapeElevation((X,Y), transform, index, elevation)


# In[19]:


def addLonLatXYtoMeasured(row, stationsLonLatXY_path):
    with open(stationsLonLatXY_path, 'rb') as f:
        stationsLonLatXY = pickle.load(f)
    station = row.stod
    values = stationsLonLatXY.get(station, [None, None, None, None])
    return pd.Series(values)


# In[20]:


def prepareMeasurements(df, stationsLonLatXY_path, decimal_places = 4):
    df = df.rename(columns = {'timi':'time'})
    df[['lon', 'lat', 'X', 'Y']] = df.apply(addLonLatXYtoMeasured, args=[stationsLonLatXY_path], axis = 1)
    df = df.round(decimal_places)
    return df


# In[17]:


def prepareRenalysis(df, decimal_places = 4):
    df = df.rename(columns = {'Wind speed':'ws', 'Wind direction': 'wd', 'Pressure':'p', 'Temperature':'t'})
    df = df.drop_duplicates(subset=['lon', 'lat', 'time', 'height_level'])
    df = df.pivot(index = ['lon', 'lat', 'time'], columns = 'height_level')
    df = df.drop(columns='yr_month')
    df.columns = [f'{col[0]}_{col[1]}' for col in df.columns]
    df = df.reset_index()
    df.time = pd.to_datetime(df.time)
    df = df.round(decimal_places)
    df[['Ri_01', 'Ri_12', 'Ri_02']] = df.apply(rowRichardson, axis = 1).apply(pd.Series)
    df[['N_01', 'N_12', 'N_02']] = df.apply(rowBruntVaisala, axis = 1).apply(pd.Series)
    df[['N_01_squared', 'N_12_squared', 'N_02_squared']] = df.apply(rowBruntVaisalaSquared, axis = 1).apply(pd.Series)
    return df


# In[7]:


def addElevation(df):

    with rasterio.open(elevation_path) as dataset:
        elevation = dataset.read(1)
        index = dataset.index
        transform = dataset.transform

    df['station_elevation'] = df.apply(addPointElevation, args = (transform, index, elevation), axis = 1)
    df['landscape_points'] = df.apply(generateLandscapeDistribution2Sectors, axis = 1)
    df['elevations']  = df.apply(generateElevationDistribution, args = (transform, index, elevation), axis = 1)

    return df


# In[22]:


def merge(measured_path = measured_path, reanalysis_path = reanalysis_path):
    measured_df = pd.read_feather(measured_path)
    reanalysis_df = pd.read_feather(reanalysis_path)
    measured_df = prepareMeasurements(measured_df, stationsLonLatXY_path)
    reanalysis_df = prepareRenalysis(reanalysis_df)
    merged_df = pd.merge(measured_df, reanalysis_df, on = ['time', 'lon', 'lat'], how = 'inner')
    merged_df[['N_01', 'N_12', 'N_02']] = merged_df[['N_01', 'N_12', 'N_02']].map(lambda x: (x.real, x.imag))
    merged_df = merged_df.drop(['fsdev', 'dsdev'], axis = 1)
    merged_df = addElevation(merged_df)

    # For some reason there are several stations that contain invalid data, maybe f and fg got switched or something, and f
    # is higher than fg. If it is something else and more errors are still in the data even after removing this. Then I don't
    # know what is going on or what I am supposed to do.
    errors = merged_df[merged_df.fg <= merged_df.f]
    merged_df = merged_df[merged_df.fg > merged_df.f]

    merged_df.to_feather(outputpath)
    errors.to_feather(outputpath_for_errors)

