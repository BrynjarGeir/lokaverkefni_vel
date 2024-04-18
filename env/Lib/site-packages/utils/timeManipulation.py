import os
from datetime import datetime, timedelta

# ChatGPT
# Round to closest 3 hour interval to match times from vedurstofa to available times from Carra
def round_to_3_hour_interval(time_str: str):
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
def round_to_3_hour_intervals(time_str: str):
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

# Given a point in time in the format that Vedurstofa provides, create two names, one for the 3 hour interval before
# And one for the three hour interval after, only one if it hits perfectly (and None to fill up)
def createCarraNameBasedOnVedurTime(vedurDateTime: str) -> list[str]:
    vedurDate, vedurTime = vedurDateTime.split(" ")
    prev, next = round_to_3_hour_intervals(vedurTime)

    nextDT = ' '.join([vedurDate, next])

    if next[:2] == "00":
        nextDateTime = datetime.strptime(nextDT, "%Y-%m-%d %H:%M:%S")
        nextDateTime += timedelta(days = 1)
        nextAns = nextDateTime.strftime("%Y-%m-%d-%H_%M")
    else:
        next = next[:5]
        next = next[:2] + "_" + next[3:]
        nextAns = '-'.join([vedurDate, next])

    
    prev = prev[:5]
    prev = prev[:2] + "_" + prev[3:]
    prevAns = '-'.join([vedurDate, prev])

    return prevAns + ".feather", nextAns + ".feather"