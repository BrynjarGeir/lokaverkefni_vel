#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd, os, dill as pickle
from tqdm.notebook import tqdm
from datetime import date
from utils.transform import getVedurLonLatInISN93
from utils.util import getTopLevelPath


# In[2]:


top_folder = getTopLevelPath() + 'data/Measured/'
stationsLonLatXY_path = top_folder + 'stationsLonLatXY.pkl'
stod_path = top_folder + 'stod.txt'
nailstripped_path = top_folder + '10min/Chunks/Nailstripped/'
filtered_path = nailstripped_path + 'Filtered_AWSL_TimeInterval/'
outputfolder = top_folder + 'Processed/'

today = date.today().strftime('%Y-%m-%d')


# In[ ]:


def createStationsLonLatXY(stod_path = stod_path, outputpath = stationsLonLatXY_path, encoding: str = 'ISO-8859-1'):
    stationsDict = {}
    with open(stod_path, 'r', encoding = encoding) as f:
        stations = [a.strip().split(',') for a in f.readlines()][1:]
        stations = [[int(a[0]), a[1], float(a[2]), float(a[3]), float(a[4]) if a[4].isnumeric() else a[4], a[5]] for a in stations]
    for station in stations:
        latitude, longitude = station[2], station[3]
        x, y = getVedurLonLatInISN93(longitude, latitude)
        stationsDict[station[0]] = (-longitude, latitude, x, y)

    with open(outputpath, 'wb') as f:
        pickle.dump(stationsDict, f)


# In[ ]:


def filter_AWSL_and_TimeInterval(nailstripped_path = nailstripped_path, threshold: str = '1 day', AWSL: int = 20):
    files = [nailstripped_path + file for file in os.listdir(nailstripped_path) if file.endswith('.feather')]
    for file in tqdm(files, total = len(files), desc = "Looping over nailstripped files..."):
        measurement_df = pd.read_feather(file)
        measurement_df = measurement_df[measurement_df.f > 20]
        filtered_data, columns, stations = [], measurement_df.columns, measurement_df.stod.unique()
        for station in tqdm(stations, total = len(stations), desc = "Looping over substations..."):
            subset_df = measurement_df[station == measurement_df.stod]
            subset_df = subset_df.reset_index(drop = True)

            while not subset_df.empty:
                idx = subset_df.f.idxmax()
                time_of_max = subset_df.iloc[idx].timi

                filtered_data.append(subset_df.iloc[idx])

                subset_df = subset_df[abs(subset_df.timi - time_of_max) >= pd.Timedelta(threshold)]

                subset_df = subset_df.reset_index(drop = True)

        filtered_df = pd.DataFrame(filtered_data, columns=columns)

        filtered_df = filtered_df.sort_values(by=['stod', 'timi'])

        filtered_df = filtered_df.reset_index(drop=True)

        outputpath = nailstripped_path + 'Filtered_AWSL_TimeInterval/' + file.split('/')[-1]

        filtered_df.to_feather(outputpath)


# In[ ]:


def combineParts(filteredWithMinAveWindSpeed_path = filtered_path):
    df, files = pd.DataFrame(), [filteredWithMinAveWindSpeed_path + file for file in os.listdir(filteredWithMinAveWindSpeed_path) if file.endswith('.feather')]

    for file in tqdm(files, total = len(files), desc = "Looping over parts to combine..."):
        if df.empty:
            df = pd.read_feather(file)
        else:
            tmp_df = pd.read_feather(file)
            df = pd.concat([df, tmp_df])
    outputpath = outputfolder + f'/measurements_{today}.feather'
    df.to_feather(outputpath)

