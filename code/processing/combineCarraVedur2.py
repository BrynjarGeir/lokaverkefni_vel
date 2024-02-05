import pandas as pd

# I'm assuming that all the carra info will be in one dataframe with lat/lon and X/Y, if not, then I will just add
# the X/Y myself before starting this, each line would contain information for all height levels and be range indexed
# If the structure is different, then I can probably just create this structure myself from the given structure

# Simply retrieve the Carra dataframe
def getCarraData(carraPath: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/allData.feather'):
    return pd.read_feather(carraPath)

def getVedurData(vedurPath: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/Stripped_25ms_24klst.feather'):
    return pd.read_feather(vedurPath)

# combines the Carra and Vedur dataframes
# Keep in mind that the carra dataframe should be larger because there are points (6) for each point from measurement
# The values for location should be accurate so we can simply calculate the points that need to be found and then look
# Them up in the carra df
def combineCarraVedur():
    carraDF, vedurDF = getCarraData(), getVedurData()

    

