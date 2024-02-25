import pandas as pd, rasterio
from time import time
from tqdm import tqdm

# I'm assuming that all the carra data will be in one feather file (dataframe) and will be indexed 

def getDTXYDFFD(row):
    return row.timi, row.X, row.Y, row.d, row.f, row.fg

#'D:/Skóli/lokaverkefni_vel/data/Carra/allCarra.feather'
def combineVedurCarraElevData(vedurPath: str = 'D:/Skóli/lokaverkefni_vel/data/Vedurstofa/Stripped_25ms_24klst_10min.feather', carraPath: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/Feather/2013-05-18-12_00.feather', tifPath: str = 'D:/Skóli/lokaverkefni_vel/data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif'):
    vedurDF = pd.read_feather(vedurPath)
    carraDF = pd.read_feather(carraPath)

    carraDF = carraDF.reset_index()

    carraDF = carraDF.drop(carraDF.index[len(vedurDF):], axis = 0)

    carraDF.time = vedurDF.timi
    carraDF.loc[:len(vedurDF), 'X'] = vedurDF.X
    carraDF.loc[:len(vedurDF), 'Y'] = vedurDF.Y


    carraVedurDF = pd.merge(vedurDF, carraDF, left_on= ['timi', 'X', 'Y'], right_on = ['time', 'X', 'Y'], how = 'inner')

    with rasterio.open(tifPath) as dataset:
        elevation = dataset.read(1)
        transform = dataset.transform
        index = dataset.index

    

    

start = time()
combineVedurCarraElevData()
end = time()

print(f"Total timelength is {end - start}")
