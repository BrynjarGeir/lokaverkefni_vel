#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from utils.util import getTopLevelPath
from datetime import date
from tqdm import tqdm, trange
import os, csv, pandas as pd


# In[ ]:


top_folder = getTopLevelPath() + 'data/Measured/'
hourly_paths = [top_folder + 'klst/', top_folder + 'vg/']
ten_min_path = top_folder + '10min/'

today = date.today().strftime('%Y-%m-%d')


# In[ ]:


def combineKLST(hourly_paths: str = hourly_paths):
    outputpath: str = top_folder + f'combined/combined_klst/combined_klst_{today}.feather'
    files = [folder + file for folder in hourly_paths for file in os.listdir(folder)]
    columns = ['timi','stod','f','fx','fg','d']
    data = []
    for file in tqdm(files, total = len(files)):
        with open(file, 'r') as f:
            lines = [line for line in csv.reader(f)]
        if 'dsdev' in lines[0]:
            lines = [line[:-1] for line in lines]
        lines = lines[1:]
        data.extend(lines)

    df = pd.DataFrame(data, columns = columns)
    df.stod = pd.to_numeric(df.stod, errors = 'coerce')
    df.timi = pd.to_datetime(df.timi, errors = 'coerce')
    df.fx = pd.to_numeric(df.fx, errors = 'coerce')
    df.f = pd.to_numeric(df.f, errors = 'coerce')
    df.fg = pd.to_numeric(df.fg, errors = 'coerce')
    df.d = pd.to_numeric(df.d, errors = 'coerce')
    df.to_feather(outputpath)


# In[ ]:


def combine10minChunks(ten_min_path: str = ten_min_path): 
    outputpath = top_folder + f'/combined_10min/Parts/'
    files = [ten_min_path + file for file in os.listdir(ten_min_path)]
    columns = None
    chunks, n = 20, len(files)
    m = n // chunks
    for chunk in trange(chunks):
        if chunk == n-1:
            cfiles = files[chunk*m:]
        else:
            cfiles = files[chunk*m:(chunk+1)*m]
        data = []
        for file in tqdm(cfiles, total = len(cfiles)):
            with open(file, 'r') as f:
                reader = list(csv.reader(f))
                
            if not columns:
                columns = reader[0]
            
            lines = reader[1:]

            data.extend(lines)
        df = pd.DataFrame(data, columns = columns)
        df.timi = pd.to_datetime(df.timi, errors = 'coerce')
        df.stod = df.stod.astype(int)
        df.f = pd.to_numeric(df.f, errors = 'coerce')
        df.fg = pd.to_numeric(df.fg, errors = 'coerce')
        df.fsdev = pd.to_numeric(df.fsdev, errors = 'coerce')
        df.d = pd.to_numeric(df.d, errors = 'coerce')
        df.dsdev = pd.to_numeric(df.dsdev, errors = 'coerce')

        df.to_feather(outputpath + 'part_' + str(chunk) + '.feather')


# In[ ]:


def combine10minText(ten_min_path: str = ten_min_path):
    outputpath: str = top_folder +  '/combined_10min.txt'
    files = [os.path.join(ten_min_path, file) for file in os.listdir(ten_min_path)]

    for file in tqdm(files, total = len(files)):
        with open(file, 'r') as f:
            lines = f.readlines()
        
        lines = lines[1:]
        with open(outputpath, 'a+') as f:
            f.writelines(lines)

