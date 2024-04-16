#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd, dill as pickle, os
from utils.calculateConstants import *
from utils.util import getTopLevelPath
from datetime import date


# In[ ]:


folder_path =  getTopLevelPath() + 'data/'
stationsLonLatXY_path = folder_path + 'Measured/stationsLonLatXY.pkl'
measured_path = folder_path + 'Measured/combined_10min/' + max(os.listdir(folder_path + 'Measured/combined_10min/'), key = lambda f: os.path.getmtime(folder_path + 'Measured/combined_10min/' + f))
reanalysis_path = folder_path + 'Reanalysis/' + max([file for file in os.listdir(folder_path + 'Reanalysis/') if file.endswith('.feather')], key = lambda f: os.path.getmtime(folder_path + 'Reanalysis/' + f))

today = date.today().strftime("%Y-%m-%d")


# In[3]:


def addXYtoMeasured(row, stationsLonLatXY_path):
    with open(stationsLonLatXY_path, 'rb') as f:
        stationsLonLatXY = pickle.load(f)
    station = row.stod
    values = stationsLonLatXY.get(station, [None, None, None, None])
    return pd.Series(values[2:])


# In[ ]:


def prepareMeasurements(df, stationsLonLatXY_path, decimal_places = 4):
    df = df.rename(columns = {'timi':'time'})
    df[['X', 'Y']] = df.apply(addXYtoMeasured, args=[stationsLonLatXY_path], axis = 1)
    df = df.round(decimal_places)
    return df


# In[ ]:


def prepareRenalysis(df, decimal_places = 4):
    df = df.rename(columns = {'lat':'Y', 'lon':'X', 'Wind speed':'ws', 'Wind direction': 'wd', 'Pressure':'p', 'Temperature':'t'})
    df = df.drop_duplicates(subset=['X', 'Y', 'time', 'height_level'])
    df = df.pivot(index = ['X', 'Y', 'time'], columns = 'height_level')
    df = df.drop(columns='yr_month')
    df.columns = [f'{col[0]}_{col[1]}' for col in df.columns]
    df = df.reset_index()
    df.time = pd.to_datetime(df.time)
    df = df.round(decimal_places)
    df[['Ri_01', 'Ri_12', 'Ri_02']] = df.apply(rowRichardson, axis = 1).apply(pd.Series)
    df[['N_01', 'N_12', 'N_02']] = df.apply(rowBruntVaisala, axis = 1).apply(pd.Series)
    df[['N_01_squared', 'N_12_squared', 'N_02_squared']] = df.apply(rowBruntVaisalaSquared, axis = 1).apply(pd.Series)
    return df


# In[ ]:


def merge(measured_path = measured_path, reanalysis_path = reanalysis_path):
    measured_df = pd.read_feather(measured_path)
    reanalysis_df = pd.read_feather(reanalysis_path)
    measured_df = prepareMeasurements(measured_df, stationsLonLatXY_path)
    reanalysis_df = prepareRenalysis(reanalysis_df)
    merged_df = pd.merge(measured_df, reanalysis_df, on = ['time', 'X', 'Y'], how = 'inner')
    merged_df[['N_01', 'N_12', 'N_02']] = merged_df[['N_01', 'N_12', 'N_02']].map(lambda x: (x.real, x.imag))
    merged_df = merged_df.drop(['fsdev', 'dsdev'], axis = 1)

    outputpath = folder_path + f'MergedMeasuredReanalysis/merged_{today}.feather'
    merged_df.to_feather(outputpath)

