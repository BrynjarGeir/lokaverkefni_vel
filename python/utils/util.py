import os
from utils.timeManipulation import createCarraNameBasedOnVedurTime
from utils.transform import readIndexBool
from get_data.getCarraBasedOnVedur import callCarra
from processing.filterAndShiftCarra import filterAndShiftFile
from math import sqrt
import pandas as pd
from tqdm import tqdm
from get_data.getCarraBasedOnVedur import callCarra

# In case I change the folder structure I can just automatically find the folder anywhere in lokaverkefni_vel
def findFile(file_name: str, directory: str= "/mnt/d/Skóli/lokaverkefni_vel/") -> str:
    for root, dirs, files in os.walk(directory):
        if file_name in files:
            return os.path.join(root, file_name)
    return None

def findFolder(folder_name: str, directory: str = "/mnt/d/Skóli/lokaverkefni_vel/") -> str:
    for root, dirs, files in os.walk(directory):
        if folder_name in dirs:
            return os.path.join(root, folder_name)
    return None

# Check if given file is present in given directory
def isFilePresent(directory: str, filename: str) -> bool:
    return filename in os.listdir(directory)

# Check if given file can be found (directory included in filePath)
def isFilePresentFilePath(filePath: str) -> bool:
    directory, filename = os.path.split(filePath)
    return isFilePresent(directory, filename)

# Find the relevant Carra files given a datetime string from vedur data, downloads and filtershifts if not available
def findRelevantCarraFiles(vedurDateTime: str) -> list[str]:
    prev, aft = createCarraNameBasedOnVedurTime(vedurDateTime)
    directory = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/"
    outputPath = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/GRIB/"

    #prevBool, aftBool = isFilePresent(directory, prev), isFilePresent(directory, aft)
    prevBool, aftBool = True, True

    if not prevBool or not aftBool:
        npoints = readIndexBool("/mnt/d/skóli/lokaverkefni_vel/data/Carra/npoints.pkl")
                
        if not prevBool:
            try:
                year, month, day, time = prev.split('-')
                time = time[:2] + ":00:00"
                file = os.path.split(prev)[1]
                file = os.path.splitext(file)[0] + ".grib"
                outputFilePath = outputPath + file           
                print(f"file: {file}, year: {year}, month: {month}, day: {day}, time: {time}, outputFilePath: {outputFilePath}")
                callCarra(day, month, year, time, outputFilePath)
                print(f"Successfully downloaded prev for {prev}. The output file path is at {outputFilePath}")
                filterAndShiftFile(file, directory, outputPath, npoints)

            except Exception as e:
                print(f"Not able to download prev at {prev}!")
                print(f"The cause being: {e}")

        if not aftBool:
            try:
                year, month, day, time = aft.split('-')
                time = time[:2] + ":00:00"
                file = os.path.split(aft)[1]
                file = os.path.splitext(file)[0] + ".grib"     
                outputFilePath = outputPath + file           
                callCarra(day, month, year, time, outputFilePath)
                print(f"Successfully downloaded aft for {aft}. The output file path is at {outputFilePath}")
                filterAndShiftFile(file, directory, outputPath, npoints, missing_variables_error_stripping, missing_variables_error_stripping_path)
            except Exception as e:
                print(f"Not able to download aft at {aft}!")
                print(f"The cause being: {e}")

    return directory + prev, directory + aft

# Return Euclidean distance between two points
def distance(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1] - b[1])**2)

# Checks if a point is a bounding point for a given point
def is_bounding_point(point, grid_point, grid_spacing):
    dx, dy = abs(grid_point[0] - point[0]), abs(grid_point[1] - point[1])
    return dx <= grid_spacing and dy <= grid_spacing

# Find the names of all files that still need to be downloaded given the stripped 10 min file of Vedurstofa data
def findFilesStillToBeDownloaded(feather_directory: str = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra", 
                                 vedurFilepath: str = "/mnt/d/Skóli/lokaverkefni_vel/data/Vedurstofa/stripped_10min.feather") -> set[str]:
    vedurDF = pd.read_feather(vedurFilepath)
    file_names = getFileNamesFromDF(vedurDF)
    already_downloaded = set([file for file in os.listdir(feather_directory) if file.endswith('.feather')])
    return file_names - already_downloaded
# Given a dataframe, look at the time series and return a set of filenames
def getFileNamesFromDF(df: pd.DataFrame) -> set[str]:
    datetimes = df['timi']
    ans = set()
    for datetime in datetimes:
        prev, aft = createCarraNameBasedOnVedurTime(datetime)
        ans.add(prev)
        ans.add(aft)
    return ans

# Download all Carra GRIB data that is still needed
def downloadCarraGRIBAndShift(rng: tuple[int], featherDirectory: str = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra", 
                      gribDirectory: str = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/GRIB",
                      npoints_path: str = "/mnt/d/skóli/lokaverkefni_vel/data/Carra/npoints.pkl") -> None:
    files = findFilesStillToBeDownloaded()
    npoints = readIndexBool(npoints_path)
    a, b = rng

    n = len(files)

    files = list(files)

    if b == None:
        files = files[a:]
    else:
        files = files[a:b]

    print(f"Found all files that are yet to be downloaded!")
    print(f"Still need to download {n} files!")
    print(f"This run looks at files in range [{a},{b if b != None else n})")

    for file in tqdm(files, total = len(files)):
        year, month, day, time, outputFilePathGRIB, filename = getVariablesNeededForCallCarra(file)
        try:
            print(f"Trying to get data for {year}-{month}-{day}-{time}")
            callCarra(day, month, year, time, outputFilePathGRIB)
            print(f"A new file should have been created at {outputFilePathGRIB}")
            filterAndShiftFile(filename, featherDirectory, gribDirectory, npoints)
        except Exception as e:
            print(f"Not able to get data with exception: {e}")

def getVariablesNeededForCallCarra(filename: str, outputDirectory: str = "/mnt/d/Skóli/lokaverkefni_vel/data/Carra/GRIB") -> list[str]:
    year, month, day, time = filename.split('-')
    time = time[:2] + ":00:00"
    file = filename.split('.')[0] + '.grib'
    outputFilePath = os.path.join(outputDirectory, file)
    print(f"OutputfilePath is {outputFilePath}")
    return year, month, day, time, outputFilePath, file

def flattenList(lst: list[list]) -> list:
    flatten_list = []
    for row in lst:
        flatten_list.extend(row)
    return flatten_list