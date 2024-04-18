#!/usr/bin/env python
# coding: utf-8

# In[2]:


from utils.transform import transformISN93ToWGS84
from utils.util import getTopLevelPath
from datetime import date
import pandas as pd, dill as pickle, json, os


# In[ ]:


top_folder = getTopLevelPath() + 'data/Measured/'
folder = 'Processed/'
file_path = max((top_folder + folder + file for file in os.listdir(top_folder + folder) if file.endswith('.feather')), key=os.path.getmtime, default=None) 
stationsLonLatXY_path = top_folder + 'stationsLonLatXY.pkl'


# In[3]:


def getDTXYD(row):
    return row.timi, row.X, row.Y, row.d


# In[4]:


def getLonLatFromXY(pointsXY):
    X, Y = [p[0] for p in pointsXY], [p[1] for p in pointsXY]
    lon, lat = transformISN93ToWGS84(X, Y)
    return lon, lat


# In[5]:


def generateJSON(coordinates, datetime):
    res = {
        datetime:
            coordinates
    }
    return res


# In[6]:


def getXY(stod, stationsLonLatXY):
    return stationsLonLatXY[stod][2:]


# In[7]:


def generateListOfDatetimesCoordinates(file_path = file_path, stations_LonLatXY_path = stationsLonLatXY_path):
    vedurDF = pd.read_feather(file_path)
    with open(stations_LonLatXY_path, 'rb') as f:
        stationsLonLatXY = pickle.load(f)

    vedurDF['X'], vedurDF['Y'] = zip(*vedurDF['stod'].apply(lambda x: getXY(x, stationsLonLatXY)))
    #vedurDF['X'], vedurDF['Y'] = zip(*vedurDF.stod.map(getXY, args = [stationsLonLatXY]))
    vedurDF = vedurDF.dropna(subset = ['timi', 'f', 'fg', 'stod', 'd', 'X', 'Y'])
    vedurDF['pointsYX'] = list(zip(vedurDF.Y, vedurDF.X))
    
    grouped_df = vedurDF.groupby('timi').agg({'pointsYX':list}).reset_index()
    grouped_df.timi = pd.to_datetime(grouped_df.timi)
    grouped_df.timi = grouped_df.timi.dt.strftime('%Y-%m-%dT%H:%M:%S')

    return grouped_df


# In[8]:


def generateAllJSON():
    today = date.today().strftime("%Y-%m-%d")
    output_path = top_folder + f'JSON/CARRA_{today}.json'
    grouped_df = generateListOfDatetimesCoordinates()
    grouped_df['JSON'] = grouped_df.apply(lambda row: generateJSON(row.pointsYX, row.timi), axis = 1)
    coords_dict = {key: value for d in grouped_df.JSON for key, value in d.items()}

    res = {"param": {"product_type": "analysis",
                     "variable": ["Wind speed", "Wind direction", "Pressure", "Temperature"],
                     "height_levels": [15,150,250,500],
                     "feather_file": "interpolatedCarra.feather"},
            "timestamp_location": coords_dict}
    
    with open(output_path, 'w') as f:
        json.dump(res, f, indent = 4)

