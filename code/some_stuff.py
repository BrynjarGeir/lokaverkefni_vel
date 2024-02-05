import os
import datetime
import pandas as pd
from utils.timeManipulation import createCarraNameBasedOnVedurTime

def get_file_modified_time(file_path):
    """
    Get the last modification time of a file.
    """
    return datetime.datetime.fromtimestamp(os.path.getmtime(file_path))

def get_estimate_total_modification_time(directory):
    """
    Estimate the total time it will take to modify all files in folder
    """
    today = datetime.datetime.now().date()
    all_files = os.listdir(directory)
    files_updated_today = [get_file_modified_time(os.path.join(directory, file)) for file in all_files if get_file_modified_time(os.path.join(directory, file)).date() == today]
    start, current = min(files_updated_today), max(files_updated_today)
    diff = current - start
    percent = len(files_updated_today) / len(all_files)
    return diff / percent, start

def findFilesStillToBeDownloaded(feather_directory, vedurFilepath) -> list[str]:
    vedurDF = pd.read_feather(vedurFilepath)

    file_names = getFileNamesFromDF(vedurDF)

    already_downloaded = os.listdir(feather_directory)

    ans = []

    for file_name in file_names:
        if file_name not in already_downloaded:
            ans.append(file_name)

    return ans




def getFileNamesFromDF(df: pd.DataFrame) -> list[str]:
    datetimes = df['timi']
    ans = set()
    for datetime in datetimes:
        prev, aft = createCarraNameBasedOnVedurTime(datetime)
        ans.add(prev)
        ans.add(aft)

    return list(ans)



#def main(directory_path):
#    # Get the current date
#    today = datetime.datetime.now().date()

#    # List all files in the directory
#    all_files = os.listdir(directory_path)

#    # Count the files updated today
#    files_updated_today = [file for file in all_files
#                           if get_file_modified_time(os.path.join(directory_path, file)).date() == today]

#    # Calculate the percentage
#    total_files = len(all_files)
#    percentage_updated_today = (len(files_updated_today) / total_files) * 100
#    total_time, start = get_estimate_total_modification_time(directory_path)

#    print(f"Total files: {total_files}")
#    print(f"Files updated today: {len(files_updated_today)}")
#    print(f"Percentage updated today: {percentage_updated_today:.2f}%")
#    print(f"The estimated total time it will take to update all the files is {total_time}")
#    print(f"This should finish around {start + total_time}")

#if __name__ == "__main__":
#    # Replace 'your_directory_path' with the path to your directory
#    directory_path = 'D:/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra/'
#    main(directory_path)


still_need_to_dwnld = findFilesStillToBeDownloaded("D:/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra", "D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stripped_10min.feather")

print(f"Number of files that still need to be downloaded is {len(still_need_to_dwnld)}")
print(f"The first five in this list are: {still_need_to_dwnld[:5]}")
