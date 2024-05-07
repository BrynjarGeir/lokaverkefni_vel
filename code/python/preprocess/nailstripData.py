#!/usr/bin/env python
# coding: utf-8

# In[2]:


from utils.util import getTopLevelPath, next_hour
from tqdm.notebook import tqdm
import os, pandas as pd


# In[3]:


folder_path = getTopLevelPath() + 'data/Measured/'
hourly_path = folder_path + 'combined_klst/' + max(os.listdir(folder_path + 'combined_klst/'), key = lambda f: os.path.getmtime(folder_path + 'combined_klst/' + f))
base10min_path = folder_path + '10min/Chunks/' 


# In[4]:


def getHourlyDf(hourly_path = hourly_path):
    hourly_df = pd.read_feather(hourly_path)
    hourly_df.stod = pd.to_numeric(hourly_df.stod, errors = 'coerce')
    hourly_df.timi = pd.to_datetime(hourly_df.timi, errors = 'coerce')
    hourly_df.fx = pd.to_numeric(hourly_df.fx, errors = 'coerce')
    hourly_df.fg = pd.to_numeric(hourly_df.fg, errors = 'coerce')
    hourly_df.f = pd.to_numeric(hourly_df.f, errors = 'coerce')
    return hourly_df


# In[7]:


def nailstripBase10min(hourly_path = hourly_path, base10min_path = base10min_path, threshold = int(1e-2)):
    hourly_df = getHourlyDf(hourly_path)
    files = [base10min_path + file for file in os.listdir(base10min_path)]
    files = [file for file in files if file.endswith('.feather')]

    for i, file in enumerate(tqdm(files, total = len(files))):
        df = pd.read_feather(file)
        df['next_hour'] = df.timi.apply(next_hour)
        hourly_df = hourly_df.rename(columns = {'timi': 'next_hour'})
        df = pd.merge(df, hourly_df, on = ['stod', 'next_hour'], how = 'inner', suffixes=('_current', '_hourly'))
        df = df[(df.f_current <= df.fx + threshold) & (df.fg_current <= df.fg_hourly)]
        df = df.drop(['f_hourly', 'fg_hourly', 'fx', 'd_hourly', 'next_hour'], axis = 1)
        df = df.rename(columns = {'f_current': 'f', 'fg_current': 'fg', 'd_current': 'd'})
        df.to_feather(base10min_path + 'Nailstripped/part_' + str(i) + '.feather')

