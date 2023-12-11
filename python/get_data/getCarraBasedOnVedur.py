import cdsapi
from pyarrow import feather
import os
from datetime import datetime, timedelta

# Get lists of what is already read and what is not available so as to not request again
def getAlreadyReadAndNotAvailable(alreadyReadPath = '/mnt/d/skóli/lokaverkefni_vel/data/Carra/GRIB', alreadyReadPathCopied = '/mnt/e/CopiedCarraGrib/', notAvailablePath = '../data/Carra/not_available.txt'):
    with open(notAvailablePath, 'r') as f:
        not_available = [line.strip() for line in f.readlines()]
    already_read = os.listdir(alreadyReadPath)
    already_read.extend(os.listdir(alreadyReadPathCopied))
    already_read = [file for file in already_read if file.endswith(".grib")]
    return already_read, not_available
    
# Request for a given list of date/times, the Carra grid
# Each item in dates/times lists correspond to each other, that is date[i], time[i] are used to make a single request
# And each of the requests only pertains to a certain moment in time (not a range of times so as to not get too much data)
def getCarraDataHeight(dates, times, outputDirectory):
    format, domain, variables = 'grib', 'west_domain', ['pressure', 'temperature', 'wind_direction', 'wind_speed']
    height_level, product_type = ['15_m', '150_m', '250_m', '500_m'], 'analysis'
    n = len(dates)

    for i in range(n):
        date, time = dates[i], times[i]

        year, month, day = date[0], date[1], date[2]

        output_filepath = createOutputFilePath(day, month, year, time, outputDirectory)

        not_available, already_read = getAlreadyReadAndNotAvailable()
        
        if output_filepath not in not_available and output_filepath not in already_read:
            try:
                callCarra(day, month, year, time, output_filepath)
            except:
                with open('../data/Carra/not_available.txt', 'a') as f:
                    f.write(output_filepath + '\n')
                print("Not available or already read!")
                
# Create outputfilepath using the time of call
def createOutputFilePath(day, month, year, time, outputDirectory):
    t = '_'.join(time.split(':'))[:-3]
    output_filepath = os.path.join(outputDirectory, '-'.join([year, month, day, t]) + ".grib")
    return output_filepath

# Makes the call for some single time and saves to file (needs to be combined later)
def callCarra(day, month, year, time, output_filepath, format = '.grid', domain = 'west_domain', variables = ['pressure', 'temperature', 'wind_direction', 'wind_speed'], 
              height_level = ['15_m', '150_m', '250_m', '500_m'], product_type = 'analysis'):

    c = cdsapi.Client()

    c.retrieve(
        'reanalysis-carra-height-levels',
        {
            'format' : format,
            'domain' : domain,
            'variable' : variables,
            'height_level' : height_level,
            'product_type' : product_type,
            'time' : time,
            'year' : year,
            'day' : day,
            'month' : month
        }, 
        output_filepath
    )

# Get the times when the wind was above some speed (20 m/s average)
# '/mnt/d/Skóli/lokaverkefni_vel/data/Vedurstofa/stripped_10min.feather'
def getDateTimeAboveVedur(filepath):
    stripped_klst = feather.read_feather(filepath)

    dates, times = [], []
    
    for index, row in stripped_klst.iterrows():
        date, time = row['timi'].split()

        year, month, day = date.split('-')

        prev, after = round_to_3_hour_intervals(time)

        dates.append((year, month, day))
        times.append(prev)

        if after == "00:00:00":
            next = (datetime.strptime('-'.join([year, month, day]), '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            year, month, day = next.split("-")
            dates.append((year, month, day))
            times.append(after)
        else:
            dates.append((year, month, day))
            times.append(after)

    return dates, times

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

#dates, times = getDateTimeAboveVedur(filepath='/mnt/d/Skóli/lokaverkefni_vel/data/Vedurstofa/stripped_10min.feather')

#dates, times  = [("2011", "01", "30")], ["15:00:00"]
#getCarraDataHeight(dates, times, "/mnt/e/")