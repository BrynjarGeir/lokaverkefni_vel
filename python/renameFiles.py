import os

folder_path = "../data/Carra/GRIB"
external_folder_path = "/mnt/e/CopiedCarraGRIB/"

def renameCarraFilesRestructure(folder_path):
    # List all files in the folder
    files = os.listdir(folder_path)
    # Iterate through the files and rename them
    for filename in files:
        parts = filename.split('_', maxsplit=3)  # Split the filename by hyphens
        if len(parts) == 4:
            day, month, year, time_extension = parts
            # Reconstruct the filename in the desired format
            new_filename = f"{year}-{month}-{day}-{time_extension}"
            # Combine the full file paths
            old_file_path = os.path.join(folder_path, filename)
            new_file_path = os.path.join(folder_path, new_filename)
            # Rename the file
            os.rename(old_file_path, new_file_path)

# ChatGPT base and then fixed
def renameCarraFilesDropSeconds(folder_path):
    files = os.listdir(folder_path)
    for filename in files:
        # Check if the file has the expected naming format
        if filename.endswith(".grib") and filename.count("_") == 2:
            fileWOEx, extension = os.path.splitext(filename)

            fileWOEx = fileWOEx[:-3]

            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, fileWOEx + extension)

            os.rename(old_path, new_path)

            print(f"Renamed from {old_path} to {new_path}!")

# ChatGPT - There were too many files in StrippedCarra directory, so I am removing the ones that don't have a corresponding
# file in the external directory CopiedCarraGRIB
def removeNonCorrespondingFiles(directory1, directory2, extension1, extension2):
    filenames1 = [os.path.splitext(file)[0] for file in os.listdir(directory1) if file.endswith(extension1)]
    filenames2 = [os.path.splitext(file)[0] for file in os.listdir(directory2) if file.endswith(extension2)]

    files_to_remove = set(filenames1) - set(filenames2)

    for filename in files_to_remove:
        file_path = os.path.join(directory1, filename + extension1)
        os.remove(file_path)
        print(f"Removed: {filename}{extension1}!")

# After deleting I want to see if the two directories are completely matching
# This is just sanity
def checkMatching(directory1, directory2, extension1, extension2):
    filenames1 = [os.path.splitext(file)[0] for file in os.listdir(directory1) if file.endswith(extension1)]
    filenames2 = [os.path.splitext(file)[0] for file in os.listdir(directory2) if file.endswith(extension2)]

    print(f"Total number of files in the local is {len(filenames1)}")
    print(f"Total number of files in the external is {len(filenames2)}")

    files_to_remove = set(filenames2) - set(filenames1)

    print(f"Total number of non matching files is {len(files_to_remove)}")
    print(f"These files are {files_to_remove}")

    
checkMatching("/mnt/d/skóli/lokaverkefni_vel/data/Carra/StrippedCarra/", "/mnt/e/CopiedCarraGRIB", ".feather", ".grib")
