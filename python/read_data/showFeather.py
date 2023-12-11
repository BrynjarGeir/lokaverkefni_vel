from pyarrow import feather
import pandas as pd
import pickle
from datetime import datetime

#df1 = feather.read_feather("/mnt/d/skóli/lokaverkefni_vel/data/Carra/StrippedCarra/2010-10-21-03_00.feather")
#df2 = feather.read_feather("/mnt/d/Skóli/lokaverkefni_vel/data/combinedTest.feather")
#indicesReadPath = "/mnt/d/Skóli/lokaverkefni_vel/data/indicesReadFromVedurDF.pkl"

#print(df1)
#print(df1.columns)

with open("/mnt/d/Skóli/lokaverkefni_vel/data/indicesReadFromVedurDF.pkl", "rb") as f:
    indices = pickle.load(f)

print(indices)


    