import cdsapi
from pyarrow import feather
import os
from datetime import datetime, timedelta
from tqdm import tqdm
from processing.filterAndShiftCarra import filterAndShiftFile
import dill as pickle

# Get lists of what is already read and what is not available so as to not request again
def getAlreadyReadAndNotAvailable(alreadyReadPath = 'D:/Skóli/lokaverkefni_vel/data/Carra/Feather/', alreadyReadPathCopied = '/mnt/e/CopiedCarraGrib', notAvailablePath = '../data/Carra/not_available.txt'):
    with open(notAvailablePath, 'r') as f:
        not_available = [line.strip() for line in f.readlines()]
    already_read = os.listdir(alreadyReadPath)
    #already_read.extend(os.listdir(alreadyReadPathCopied))
    already_read = [file for file in already_read if file.endswith(".feather")]
    already_read = [file.split('.')[0] for file in already_read]
    already_read = [file.split('-') for file in already_read]
    already_read = [tuple([dt[0], dt[1], dt[2], dt[3][:2]+':00:00']) for dt in already_read]
    return set(already_read), set(not_available)
    
# Request for a given list of date/times, the Carra grid
# Each item in dates/times lists correspond to each other, that is date[i], time[i] are used to make a single request
# And each of the requests only pertains to a certain moment in time (not a range of times so as to not get too much data)
def getCarraDataHeight(dateTimes, outputDirectory, feather_directory = "D:/Skóli/lokaverkefni_vel/data/Carra/Feather/"):
    n = len(dateTimes)

    for dt in tqdm(dateTimes, total = n):

        year, month, day, time = dt

        output_filepath = createOutputFilePath(day, month, year, time, outputDirectory)
        file = createFileName(day, month, year, time) + '.grib'
        
        #if output_filepath not in already_read:
        try:
            callCarra(day, month, year, time, output_filepath)
            filterAndShiftFile(file, feather_directory, outputDirectory)
        except:
            print("Not available or already read!")
                    
# Create outputfilepath using the time of call
def createOutputFilePath(day, month, year, time, outputDirectory) -> str:
    filename = createFileName(day, month, year, time)
    output_filepath = os.path.join(outputDirectory, filename + ".grib")
    return output_filepath

# Does not include file extension (so that can be set for each case)
def createFileName(day, month, year, time) -> str:
    t = '_'.join(time.split(':'))[:-3]
    filename = '-'.join([year, month, day, t])
    return filename

# Makes the call for some single time and saves to file (needs to be combined later)
def callCarra(day, month, year, time, output_filepath, format = 'grib', domain = 'west_domain', variables = ['pressure', 'temperature', 'wind_direction', 'wind_speed'], 
              height_level = ['15_m', '150_m', '250_m', '500_m'], product_type = 'analysis', grid = [0.04180602,0.01826484], area = [66.6, -24.6, 63.3, -13.4]):

    c = cdsapi.Client()

    c.retrieve(
        'reanalysis-carra-height-levels',
        {
            'domain': domain,
            'variable': variables,
            'height_level': height_level,
            'product_type': product_type,
            'time': time,
            'year': year,
            'month': month,
            'day': day,
            'format': format,
            'grid': grid,
            'area': area
        }, 
        output_filepath
    )

# Get the times when the wind was above some speed (20 m/s average)
# 'D:/Skóli/lokaverkefni_vel/data/Vedurstofa/stripped_10min.feather'
def getDateTimeAboveVedur(filepath, already_read: list[tuple]):
    stripped_10min = feather.read_feather(filepath)

    dateTimes = []
    
    for index, row in tqdm(stripped_10min.iterrows(), total = len(stripped_10min)):
        date, time = row['timi'].split()

        year, month, day = date.split('-')

        prev, aft = round_to_3_hour_intervals(time)

        dateTimes.append((year, month, day, prev))

        if aft == "00:00:00":
            next = (datetime.strptime('-'.join([year, month, day]), '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            year, month, day = next.split("-")
            dateTimes.append((year, month, day, aft))
        else:
            dateTimes.append((year, month, day, aft))

    dateTimes = set(dateTimes)
    dateTimes = dateTimes.difference(already_read)

    return dateTimes

# ChatGPT
# Round to closest 3 hour interval to match times from vedurstofa to available times from Carra
def round_to_3_hour_interval(time_str):
    # Convert time to minutes
    hours, minutes, _ = map(int, time_str.split(":"))
    total_minutes = hours * 60 + minutes

    # Calculate the closest 3-hour interval in minutes
    closest_interval_minutes = (total_minutes + 90) // 180 * 180

    # Convert the interval back to hh:mm format
    # Don't need seconds
    hours, minutes = divmod(closest_interval_minutes, 60)
    if hours == 24:
        hours = 0
    return f"{hours:02d}:{minutes:02d}"

# ChatGPT
# Does the same as above but gives both 3 hour before and after for bridging
def round_to_3_hour_intervals(time_str):
    # Convert time to minutes
    hours, minutes, _ = map(int, time_str.split(":"))
    total_minutes = hours * 60 + minutes

    # Calculate the closest 3-hour intervals in minutes
    previous_interval_minutes = (total_minutes // 180) * 180
    next_interval_minutes = previous_interval_minutes + 180

    # Convert the intervals back to hh:mm format
    prev_hours, prev_minutes = divmod(previous_interval_minutes, 60)
    next_hours, next_minutes = divmod(next_interval_minutes, 60)

    if next_hours == 24:
        next_hours = 0

    return (f"{prev_hours:02d}:{prev_minutes:02d}:00", f"{next_hours:02d}:{next_minutes:02d}:00")

#ChatGPT, validate DateTime
def is_valid_date_time(day = "01", month = "01", year = "2000", time = "00:00:00"):
    try:
        day = int(day)
        month = int(month)
        year = int(year)
        hours, minutes, seconds = map(int, time.split(':'))

        if 1 <= month <= 12 and 1 <= day <= 31 and 0 <= hours < 24 and 0 <= minutes < 60 and 0 <= seconds < 60:
            return True
        else:
            return False
    except ValueError:
        return False

# Retrive last pickled datetimes to be downloaded
def getPickledDateTimes(dtPath: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/carraDTNeeded.pkl'):
    with open(dtPath, 'rb') as f:
        dateTimes = pickle.load(f)
    return dateTimes

# Create a set in a pickled file that saves the currently needed datetimes (datetime is a tuple like (year, month, day, time))
def createPickledDateTimes(dtPath: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/carraDTNeeded.pkl', featherPath: str = 'D:/Skóli/lokaverkefni_vel/data/Vedurstofa/Stripped_20ms_10min.feather'):
    already_read, _ = getAlreadyReadAndNotAvailable()
    dateTimes = getDateTimeAboveVedur(filepath=featherPath, already_read=already_read)

    with open(dtPath, 'wb') as f:
        pickle.dump(dateTimes, f)

#dateTimes = getPickledDateTimes()
#getCarraDataHeight(dateTimes, "D:/Skóli/lokaverkefni_vel/data/Carra/GRIB/") #"/mnt/e/CopiedCarraGRIB/"

#createPickledDateTimes()