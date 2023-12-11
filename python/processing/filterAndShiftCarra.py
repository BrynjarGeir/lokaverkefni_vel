from utils.transform import dropOutOfRange, readCarraGRIBIntoDataframe, readIndexBool, transformCoordinatesFromShiftedWSG84ToISN93WithinDF
import os
from time import time

# Drop rows from Carra data in GRIB files and output to feather
def dropToFeather(GRIBPATH: str = "/mnt/e/CopiedCarraGRIB/", outputDirectory: str = "/mnt/d/skóli/lokaverkefni_vel/data/Carra/StrippedCarra/", 
                    npoints_path: str = "/mnt/d/skóli/lokaverkefni_vel/data/Carra/npoints.pkl"): # GRIBPATH = "/mnt/d/skóli/lokaverkefni_vel/data/Carra/GRIB/", 
    files = os.listdir(GRIBPATH)

    files = [file for file in files if file.endswith(".grib")]

    npoints = readIndexBool(npoints_path)

    missing_variables_error_stripping_path = "/mnt/d/skóli/lokaverkefni_vel/data/Carra/missing_variables_error_stripping.txt"
    with open(missing_variables_error_stripping_path) as f:
        missing_variables_error_stripping = f.readlines()

    for file in files:
        filterAndShiftFile(file, outputDirectory, GRIBPATH, npoints, missing_variables_error_stripping, missing_variables_error_stripping_path)

# Split up function so as to be able to call it for a given file
def filterAndShiftFile(file: str, outputDirectory: str, GRIBPATH: str, npoints: list) -> None:
    filename = file.split(".")[0] + ".feather"
    
    try:
        df = readCarraGRIBIntoDataframe(os.path.join(GRIBPATH, file))
        df = dropOutOfRange(df, npoints)

        df = transformCoordinatesFromShiftedWSG84ToISN93WithinDF(df)

        outputPath = os.path.join(outputDirectory, filename)

        #if os.path.exists(outputPath):
        #    print(f"Outputpath {outputPath} already exists!")
        #else:
        df.to_feather(outputPath)
        print(f"A new file at {outputPath} should have been created!")
    except KeyError as e:
        print(f"Not able to filter and shift {file}.")

