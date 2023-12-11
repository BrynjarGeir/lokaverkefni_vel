import pandas as pd
from pyarrow import feather, dataset, table

df = feather.read_feather('../data/Vedurstofa/stripped_10min.feather')


print(df)