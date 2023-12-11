from pyarrow import feather
from get_data.getCarraBasedOnVedur import callCarra
from processing.filterAndShiftCarra import filterAndShiftFile
from utils.transform import readIndexBool
from datetime import datetime
import os
import csv
import pandas as pd
from tqdm import tqdm


def findCorrupted():
    featherDirectory = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/"
    gribDirectory = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/GRIB/"

    files = os.listdir(featherDirectory)

    index = files.index("2019-10-04-06_00.feather")

    files = files[index:]

    need_to_download_again = []

    for i, file in enumerate(files):
        try:
            df = feather.read_feather(os.path.join(featherDirectory, file))
        except Exception as e:
            filename = os.path.splitext(file)[0]
            output_filepath = os.path.join(gribDirectory, filename + ".grib")
            #callCarra(format, domain, variables, height_level, product_type, day, month, year, t, output_filepath)
            need_to_download_again.append(output_filepath)
        if not i % 100:
            print(f"At {i+1} of {len(files)}.")
            print(f"Length of corrupted list is {len(need_to_download_again)}")
    with open("/mnt/d/Skóli/lokaverkefni_vel/data/Carra/need_to_download_again_GRIB.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerows(need_to_download_again)

def callNewGRIB(indices):
    featherDirectory = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/"
    gribDirectory = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/GRIB/"

    format, domain, variables = 'grib', 'west_domain', ['pressure', 'temperature', 'wind_direction', 'wind_speed']
    height_level, product_type = ['15_m', '150_m', '250_m', '500_m'], 'analysis'

    with open("/mnt/d/Skóli/lokaverkefni_vel/data/Carra/need_to_download_again_GRIB.csv", "r") as f:
        files = list(csv.reader(f))
        files = [''.join(file) for file in files]
        
    s, e = indices
    files = files[s:e+1]
    for file in files:
        year, month, day, t = file.split('-')
        year = year.split('/')[-1]
        feather_name = os.path.splitext(file)[0] + '.feather'
        t = t[:2] + ":00:00"
        outputPath = os.path.join(featherDirectory, feather_name)

        try:
            callCarra(format, domain, variables, height_level, product_type, day, month, year, t, outputPath)
            print(f"A new file should have been created at {outputPath}")
        except Exception as e:
            print(f"A file could not be created at {outputPath}")

def filterAndShiftNewGRIBToFeatherFiles():
    featherDirectory = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/"
    gribDirectory = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/GRIB/"

    files = os.listdir(gribDirectory)
    npoints_path = "/mnt/d/skóli/lokaverkefni_vel/data/Carra/npoints.pkl"
    npoints = readIndexBool(npoints_path)
    missing_variables_error_stripping_path = "/mnt/d/skóli/lokaverkefni_vel/data/Carra/missing_variables_error_stripping.txt"
    with open(missing_variables_error_stripping_path) as f:
        missing_variables_error_stripping = f.readlines()

    for file in files:
        filterAndShiftFile(file, featherDirectory, gribDirectory, npoints, missing_variables_error_stripping, missing_variables_error_stripping_path)

def changeFileExtension(directory: str, fro: str, too: str) -> None:
    files = os.listdir(directory)

    for file in files:
        if file.endswith(fro):
            newname = os.path.splitext(file)[0]
            newname = os.path.join(directory, newname + too)
            oldname = os.path.join(directory, file)
            print(f"oldname: {oldname}, newname: {newname}")
            os.rename(oldname, newname)

def drop_level_recent_files(feather_directory, days_threshold = 1):
    feather_files = [file for file in os.listdir(feather_directory) if file.endswith(".feather")]
    current_date = datetime.now()
    recent_files = [
        file for file in feather_files
        if (current_date - datetime.fromtimestamp(os.path.getmtime(os.path.join(feather_directory, file)))).days <= days_threshold
    ]

    for file in tqdm(recent_files, total=len(recent_files)):
        file_path = os.path.join(feather_directory, file)
        df = pd.read_feather(file_path)
        if 'index' in df.columns:
            df.drop('index', axis = 1)
        if 'level_0' in df.columns:
            df.drop('level_0', axis = 1)
        if isinstance(df.index, pd.MultiIndex):
            df = df.reset_index()
        df.to_feather(file_path)

#findCorrupted()

#callNewGRIB((101, 137))

#changeFileExtension("/mnt/d/Skóli/lokaverkefni_vel/data/Carra/GRIB/", ".feather", ".grib")

#filterAndShiftNewGRIBToFeatherFiles()

drop_level_recent_files("/mnt/d/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra")