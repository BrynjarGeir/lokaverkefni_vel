import pandas as pd
import os

def resetIndexAllCarraFeather(directory = "D:/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/"):

    files = os.listdir(directory)

    for file in files:
        df = pd.read_feather(directory + file)

        df = df.reset_index()
    
        df.to_feather(directory + file)


resetIndexAllCarraFeather()