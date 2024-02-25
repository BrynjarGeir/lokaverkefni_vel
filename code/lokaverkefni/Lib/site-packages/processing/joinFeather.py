import os
import pandas as pd
from pyarrow import feather, concat_tables

def joinFeather(directoryPath):
    files = [f for f in os.listdir(directoryPath) if f.endswith('.feather')]
    combined_table = None

    for file in files:
        file_path = os.path.join(directoryPath,file)
        data = feather.read_table(file_path)    

        if combined_table == None and len(data) != 0:
            combined_table = data
        elif len(data) != 0:
            combined_table = concat_tables([combined_table, data])


    combined_file_path = '../data/Vedurstofa/' + directoryPath.split('/')[-1] + '.feather'
    feather.write_feather(combined_table, combined_file_path)

    print(f"Combined {len(files)} Feather files into {combined_file_path}")


#joinFeather('../data/Vedurstofa/stripped_10min')

df = pd.read_feather('../data/Vedurstofa/stripped_10min.feather')

print(df)