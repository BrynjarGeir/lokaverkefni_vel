from pyarrow import feather
import pandas as pd, numpy as np, rasterio
from pprint import pprint as pp
from utils.transform import transformISN93ToWGS84

#df1 = feather.read_feather("D:Skóli/lokaverkefni_vel/data/Vedurstofa/nStripped_10min.feather")
df2 = feather.read_feather("D:/Skóli/lokaverkefni_vel/data/combined-29-1-24.feather")

print(df2)
print(df2.columns)

#df2.rename(columns = {'lat': 'Y', 'lon': 'X'}, inplace = True)

#lons, lats = transformISN93ToWGS84(df2.X, df2.Y)

#df2['longitude'], df2['latitude'] = lons, lats

#with rasterio.open('D:/Skóli/lokaverkefni_vel/data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif') as dataset:
#    index = dataset.index

#y, x = zip(*map(index, df2.X, df2.Y))

#df2['y'], df2['x'] = y, x

#df2.DateTime = pd.to_datetime(df2.DateTime)

#df2.set_index(['DateTime', 'y', 'x'], inplace = True)

#df2.to_feather('D:/Skóli/lokaverkefni_vel/data/combined-29-1-24.feather')