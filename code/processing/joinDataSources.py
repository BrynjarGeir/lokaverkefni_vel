import pandas as pd
from utils.calculateConstants import *
import json

with open("D:/SKóli/lokaverkefni_vel/data/carra24klst-25-2-24-test3months.json", 'r') as f:
    jsn = json.load(f)
X,Y = [], []
for timestamp in jsn['timestamp_location']:
    X.append(jsn['timestamp_location'][timestamp][0][0])
    Y.append(jsn['timestamp_location'][timestamp][0][1])

#df1 = pd.read_feather('E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/Stripped_25ms_24klst_10min.feather')

#df2 = pd.read_feather('E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/interpolatedCarra-full-25ms-24hr.feather')
    
df1 = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/Vedurstofa/Stripped_25ms_24klst_10min.feather')

df2 = pd.read_feather('D:/Skóli/lokaverkefni_vel/data/interpolatedCarra-test-1month-26-2-24.feather')

df1 = df1.rename(columns = {'timi':'time'})

df1.time = pd.to_datetime(df1.time)
df1.time = df1.time.dt.strftime('%Y-%m-%dT%H:%M:%S')
df1 = df1.drop_duplicates()

df2 = df2.rename(columns = {'lat':'Y', 'lon':'X', 'Wind speed':'ws', 'Wind direction': 'wd', 'Pressure':'p', 'Temperature':'t'})
df2 = df2.drop_duplicates()

df2 = df2.pivot(index = ['X', 'Y', 'time'], columns = 'height_level')
df2 = df2.drop(columns='yr_month')

df2.columns = [f'{col[0]}_{col[1]}' for col in df2.columns]
df2 = df2.reset_index()

decimal_places = 4

df1 = df1.round(decimal_places)
df2 = df2.round(decimal_places)

df1 = df1.sort_values(by='X')
df2 = df2.sort_values(by='Y')

df = pd.merge(df2, df1, on = ['time', 'X', 'Y'], how = 'inner')

df = df.filter(regex = '^(?!.*_150$)', axis = 1)

df[['Ri_01', 'Ri_12']] = df.apply(rowRichardson, axis = 1).apply(pd.Series)
df[['N_01', 'N_12']] = df.apply(rowBruntVaisala, axis = 1).apply(pd.Series)

df.to_feather('D:/Skóli/lokaverkefni_vel/data/merged-test1month-26-2-24.feather')