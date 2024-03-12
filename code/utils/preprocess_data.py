import pandas as pd, numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# Returns a 60/20/20 train/val/test split
def prepareData(dataPath: str = 'E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/merged-w-landscape-full-25ms-24hr-28-2-24.feather'):
    df = pd.read_feather(dataPath)

