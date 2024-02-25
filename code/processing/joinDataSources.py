import pandas as pd
from utils.transform import transformISN93ToWGS84

df1 = pd.read_feather('E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/Stripped_25ms_24klst_10min.feather')

df2 = pd.read_feather('E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/interpolatedCarra-full-25ms-24hr.feather')

df1 = df1.rename(columns = {'timi':'time'})

df1.time = pd.to_datetime(df1.time)
df1.time = df1.time.dt.strftime('%Y-%m-%dT%H:%M:%S')
df1 = df1.drop_duplicates()

df2 = df2.rename(columns = {'lat':'Y', 'lon':'X', 'Wind speed':'ws', 'Wind direction': 'wd', 'Pressure':'p', 'Temperature':'t'})
df2 = df2.drop_duplicates()

print(df2.X.unique())
print(len(df2.X.unique()))

print(100*len(df2.X.unique())/len(df2))

exit()

df2 = df2.pivot(index = ['X', 'Y', 'time'], columns = 'height_level')
df2 = df2.drop(columns='yr_month')

df2.columns = [f'{col[0]}_{col[1]}' for col in df2.columns]
df2 = df2.reset_index()

#print(df1.sort_values(by='X'))
#print(df2.sort_values(by='X'))

def find_closest_index(x, df, column_name):
    return (abs(df[column_name]-x)).idxmin()

df2['closest_index_df1'] = df2.X.apply(find_closest_index, args = (df1, 'X'))

df = pd.merge(df2, df1, on = ['time', 'X', 'Y'], how = 'inner')

print(df)