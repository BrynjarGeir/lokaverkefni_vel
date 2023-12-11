import xarray as xr
import pandas as pd

def readCarraGRIBIntoDataset(filepath):
    ds = xr.open_dataset(filepath, engine = 'cfgrib')
    return ds

def setupDataFramesForCarraDataset(ds):
    dataframes = {}

    for var_name in ['wdir', 't', 'ws', 'pres']:
        df = ds[var_name].to_dataframe()

        dataframes[var_name] = df
    combined_df = pd.concat(dataframes, axis = 1, join = 'outer')
    combined_df.columns = combined_df.columns.droplevel()
    combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]
    return combined_df

def readCarraGRIBIntoDataframe(filepath):
    ds = readCarraGRIBIntoDataset(filepath)
    return setupDataFramesForCarraDataset(ds)