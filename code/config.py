import os

class Config:
    def __init__(self):
        self.merged_data_path = self.get_merged_data_path()

    def get_merged_data_path(self):
        computer_name = os.environ['COMPUTERNAME']
        if 'BRYNJARGEIRSLAP' == computer_name:
            return 'D:\Skóli\lokaverkefni_vel\data\merged-full-W-Landscape-And-Station-Elevations-25ms-24hr-11-3-24.feather'
        else:
            return 'E:/Skóli/HÍ/Vélaverkfræði Master HÍ/Lokaverkefni/Data/merged-full-W-Landscape-And-Station-Elevations-25ms-24hr-11-3-24.feather'
        
config = Config()