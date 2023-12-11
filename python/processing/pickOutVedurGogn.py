import pandas as pd
from pyarrow import feather
import os

# Still needs to be implemented: adding clause to check when the 10 min max over hour doesn't match the hour max (probably 0)

# Given a minimum for a given column (like wind speed or gust) select only the lines that adhere to that
# and write to feather file for a given station
def selectFromStation(filepath, wFilePath, band = 2, limit = 20):
    with open(filepath) as f:
        line = f.readline().strip()
        header = line.rstrip().split(',')
        df = pd.DataFrame(columns=header)
        numberOfMathces, total_lines = 0, 0
        line = f.readline()
        while line:
            data = line.split(',')
            if data[2].isnumeric() and float(data[band]) >= limit:
                data[-1] = data[-1].strip()
                df.loc[len(df.index)] = data
                numberOfMathces += 1
            total_lines += 1
            line = f.readline()
        df.reset_index(drop=True, inplace=True)
        feather.write_feather(df, wFilePath + '.feather')

        return numberOfMathces, total_lines

# Given a directory with the station files and an output directory select the lines that match for every station and create
# Feather files
def stripData(commonPath, directory, outputDirectory):
    directory = commonPath + directory
    outputDirectory = commonPath + outputDirectory
    files = os.listdir(directory)
    for filename in files:
        station = filename.split('.')
        wFileName = station[0] + '_stripped'
        selectFromStation(directory+filename, outputDirectory + wFileName)
# Call stripData for all types of station data (10 min vedurstofa, klst vedurstofa and vegagerdin)
def stripAllData():
    commonPath = "/mnt/d/Skóli/lokaverkefni_vel/data/Vedurstofa/"
    stripData(commonPath, '10min/', 'selected_10min/')
    stripData(commonPath, 'klst/', 'selected_klst/')
    stripData(commonPath, 'vg/', 'selected_vg/')

stripAllData()