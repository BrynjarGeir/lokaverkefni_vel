import os
import csv
from utils.util import find_folder

def createFileList(folder_name = "GRIB", output_filename = "filelistGRIB.csv", output_fileDirectory = "Carra"):
    folderPath = find_folder(folder_name)
    outputFolderPath = find_folder(output_fileDirectory)

    files = os.listdir(folderPath)

    with open(os.path.join(outputFolderPath, output_filename), 'w', newline = '') as file:
        csv_writer = csv.writer(file, delimiter=' ')

        csv_writer.writerows(files)

createFileList()