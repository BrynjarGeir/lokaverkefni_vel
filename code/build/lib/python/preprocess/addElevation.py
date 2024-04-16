#!/usr/bin/env python
# coding: utf-8

# # Generate landscape and elevation points for a dataframe that already contains the Veðurstofu measurement and Carra reanalysis
# 
# The type of landscape distribution to be generated can be changed by changing the imports from utils.elevation

# In[2]:


from utils.elevation import generateLandscapeDistribution2Sectors, generateElevationDistribution, findLandscapeElevation
from utils.util import getTopLevelPath
from datetime import date

import pandas as pd, rasterio, os


# In[2]:


folder_path = getTopLevelPath() + 'data/'
mergedMeasuredReanalysis = folder_path + 'MergedMeasureReanalysis/' + max(os.listdir(folder_path + 'MergedMeasureReanalysis/'), key = lambda f: os.path.getmtime(folder_path + 'MergedMeasureReanalysis/' + f))
elevation_path = folder_path + "Elevation/IslandsDEMv1.0_20x20m_isn93_zmasl.tif"
today = date.today().strftime("%Y-%m-%d")
outputpath = folder_path + f'Ready/data_{today}.feather'


# In[4]:


def addPointElevation(row, transform, index, elevation):
    X, Y = row.X, row.Y
    return findLandscapeElevation((X,Y), transform, index, elevation)


# In[ ]:


def addElevation():
    df = pd.read_feather(mergedMeasuredReanalysis)

    with rasterio.open(elevation_path) as dataset:
        elevation = dataset.read(1)
        index = dataset.index
        transform = dataset.transform

    df['station_elevation'] = df.apply(addPointElevation, args = (transform, index, elevation), axis = 1)
    df['landscape_points'] = df.apply(generateLandscapeDistribution2Sectors, axis = 1)
    df['elevations']  = df.apply(generateElevationDistribution, args = (transform, index, elevation), axis = 1)

    df.to_feather(outputpath)

