from utils.timeManipulation import createCarraNameBasedOnVedurTime, round_to_3_hour_intervals
from utils.util import allPresentFeatherFiles
from utils.interpolate import findBoundingPoints

from get_data.getCarraBasedOnVedur import callCarra, createOutputFilePath
from get_data.generateJSONForCarra import generateListOfDatetimesCoordinates

from process_data.filterAndShiftCarra import filterAndShiftFile
from process_data.combineCarraVedur import bridgeForHeightLevel, combineHeightLevelsCarraVedur


from tqdm import tqdm
import os, pandas as pd

datetimeLocation = generateListOfDatetimesCoordinates()

# pick out points and bridge for each of the carra feather files and call carra if missing
def singleOutCarra(featherPath: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/Feather/', gribPath: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/GRIB'):
    allfeatherfiles, combined = allPresentFeatherFiles(), []
    for index, row in tqdm(datetimeLocation.iterrows(), total = len(datetimeLocation)):
        vedurDatetime = row.timi.strftime("%Y-%m-%d %H:%M:%S")
        prev, aft = createCarraNameBasedOnVedurTime(vedurDatetime)

        if prev not in allfeatherfiles:
            date, time = vedurDatetime.split()

            year, month, day = date.split('-')

            prev_time, _ = round_to_3_hour_intervals(time)

            output_filepath = createOutputFilePath(day, month, year, prev_time, gribPath)
            
            callCarra(day, month, year, prev_time, output_filepath)
            filterAndShiftFile(prev, featherPath, gribPath)

            allfeatherfiles.append(prev)

        if aft not in allfeatherfiles:
            date, time = vedurDatetime.split()

            year, month, day = date.split('-')

            _, aft_time = round_to_3_hour_intervals(time)

            output_filepath = createOutputFilePath(day, month, year, aft_time, gribPath)
            
            callCarra(day, month, year, aft_time, output_filepath)
            filterAndShiftFile(aft, featherPath, gribPath)

            allfeatherfiles.append(aft)

        prev_df, aft_df = pd.read_feather(os.path.join(featherPath, prev)), pd.read_feather(os.path.join(featherPath, aft))

        for points in row.pointsXY:
            boundingPoints_prev = [findBoundingPoints(point, prev_df) for point in points]
            boundingPoints_aft = [findBoundingPoints(point, aft_df) for point in points]

            n = len(boundingPoints_aft)

            for i in range(n):
                bP15_prev, bP150_prev, bP250_prev, bP500_prev = boundingPoints_prev[i]
                bP15_aft, bP150_aft, bP250_aft, bP500_aft = boundingPoints_aft[i]

                bridged15 = bridgeForHeightLevel(bP15_prev, bP15_aft, prev_df, aft_df, points[i][0], points[i][1], ["wdir", "t", "ws", "pres"], vedurDatetime, 15.0)
                bridged150 = bridgeForHeightLevel(bP150_prev, bP150_aft, prev_df, aft_df, points[i][0], points[i][1], ["wdir", "t", "ws", "pres"], vedurDatetime, 150.0)
                bridged250 = bridgeForHeightLevel(bP250_prev, bP250_aft, prev_df, aft_df, points[i][0], points[i][1], ["wdir", "t", "ws", "pres"], vedurDatetime, 250.0)
                bridged500 = bridgeForHeightLevel(bP500_prev, bP500_aft, prev_df, aft_df, points[i][0], points[i][1], ["wdir", "t", "ws", "pres"], vedurDatetime, 500.0)

                comb = combineHeightLevelsCarraVedur(bridged15, bridged150, bridged250, bridged500)
                combined.append(comb)
        if not index % 1000:
            df = pd.DataFrame(combined, columns = ['DateTime', 'lat', 'lon', 'wdir15', 't15', 'ws15', 'pres15', 'wdir150', 't150', 'ws150', 'pres150', 'wdir250', 't250', 'ws250', 'pres250', 'wdir500', 't500', 'ws500', 'pres500'])

            df.to_feather('D:/Skóli/lokaverkefni_vel/data/combined-1-2-24.feather')



    df = pd.DataFrame(combined, columns = ['DateTime', 'lat', 'lon', 'wdir15', 't15', 'ws15', 'pres15', 'wdir150', 't150', 'ws150', 'pres150', 'wdir250', 't250', 'ws250', 'pres250', 'wdir500', 't500', 'ws500', 'pres500'])

    df.to_feather('D:/Skóli/lokaverkefni_vel/data/combined-1-2-24.feather')


singleOutCarra()