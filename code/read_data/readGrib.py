import xarray as xr
import pandas as pd
import os
import shutil

folder_path = '../data/Carra/GRIB/'

def setupDataFrames(ds):
    dataframes = {}

    for var_name in ['wdir', 't', 'ws', 'pres']:
        df = ds[var_name].to_dataframe()
        dataframes[var_name] = df

    combined_df = pd.concat(dataframes, axis = 1, join = 'outer')
    combined_df.columns = combined_df.columns.droplevel()
    combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]
    
    return combined_df

def showDataset(file_path):
    try:
        ds = xr.open_dataset(file_path, engine='cfgrib')
        lats = ds.latitude.values.flatten()
        lons = ds.longitude.values.flatten()
        print((min(lats), max(lats)))
        print((min(lons), max(lons)))

    except EOFError as e:
        print(f"Not able to open dataset from file {file_path}. Possibly corrupted!")

def showDatasets(directory):
    files = os.listdir(directory)

    for file in files:
        showDataset(os.path.join(directory, file))