from pyarrow import feather
import pandas as pd, numpy as np

#df1 = feather.read_feather("/mnt/d/skóli/lokaverkefni_vel/data/Vedurstofa/stripped_10min.feather")
#df2 = feather.read_feather(/combinedTest.feather")
df3 = feather.read_feather("/mnt/d/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/2023-09-30-18_00.feather")
#indicesReadPath = "/mnt/d/Skóli/lokaverkefni_vel/data/indicesReadFromVedurDF.pkl"

#print("stripped 10 min shape:", df1.shape)

#print("combined Test", df2.shape)

print(df3)

exit()
df1.set_index(['timi', 'lat', 'lon'], inplace = True)
df1.rename_axis(index={'timi':'DateTime'}, inplace = True)
df2.set_index(['DateTime', 'lat', 'lon'], inplace = True)

merged_df = pd.merge(df1, df2, left_index=True, right_index=True, how='inner', indicator=True)

matched_count = (merged_df['_merge'] == 'both').sum()
print(f"Number of matching indices is {matched_count}")

merged_df.drop(['_merge'], inplace=True)

fgList = pd.Series([float(i) for i in list(merged_df['fg'])])
fList = pd.Series([float(i) for i in list(merged_df['f'])])
factors = [x / y for x,y in zip(fgList, fList)]

merged_df['fg'] = pd.to_numeric(merged_df['fg'])
merged_df['f'] = pd.to_numeric(merged_df['f'])
merged_df['d'] = pd.to_numeric(merged_df['d'])
merged_df['gust_factor'] = factors

merged_df.attrs['Description'] = "This dataframe is updated so to include f, fg and the calculated gust factor. It cuts down some rows from earlier because for some reason there was not always match between combinedTest and stripped_10 min <when looking at the index of DateTime/lat/lon. That is now it is multiindexed by DateTime and location."

merged_df.to_feather('/mnt/d/Skóli/lokaverkefni_vel/data/combined-4-1-24.feather')