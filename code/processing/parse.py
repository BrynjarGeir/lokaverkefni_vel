import numpy as np
import pandas as pd
import chardet

file = input("Input relative file path of file to read: ")
delim = input("Give delimiter of file:  ")

def readStations(file = "./data/stod.txt", delim = ",", header_row = 0):
    with open(file, 'rb') as f:
        result = chardet.detect(f.read())
    stations = pd.read_csv(file, sep = delim, header = header_row, encoding=result['encoding'])
    ret = {}

    for index, station in stations.iterrows():
        stod, lengd, breidd = stations.at[index, "stod"], stations.at[index, "lengd"], stations.at[index, "breidd"]

        ret[stod] = (lengd, breidd)
    return ret
    
def addLocationToMeasurements(file, stations = "./data/stod.txt", delim = ",", header_row = 0):
    with open(stations, "rb") as f:
        result = chardet.detect(f.read())
    df_stations = pd.read_csv(stations, sep = delim, header = header_row, encoding = result["encoding"])
    print("Number of stations are: ", len(df_stations))
    df_file = pd.read_csv(file, sep = delim, header = header_row)

    result_df = df_file.merge(df_stations, on='stod', how='left')

    return result_df

df = addLocationToMeasurements(file)

df = df.dropna()

print("Done parsing!")

y = df["fg"]

df = df.drop(["stod", "nafn", "timi", "fg", "skst"], axis = 1)

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

X_train, X_test, y_train, y_test = train_test_split(df, y, test_size=0.2, random_state=42)

model = LinearRegression()

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

mse = mean_squared_error(y_test, y_pred)

r2 = r2_score(y_test, y_pred)

print("mse: ", mse)
print("r2:  ", r2)