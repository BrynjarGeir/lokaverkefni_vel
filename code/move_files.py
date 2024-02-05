import os
import shutil
from tqdm import tqdm

def move_files_to_seagate(grib_dir, feather_dir, grib_extension, feather_extension, target_dir):
    grib_files = [f for f in os.listdir(grib_dir) if f.endswith(grib_extension)]
    feather_files = [f for f in os.listdir(feather_dir) if f.endswith(feather_extension)]
    #already_moved = [f for f in os.listdir(target_dir) if f.endswith(grib_extension)]

    for grib_file in tqdm(grib_files, total = len(grib_files)):
        move_file_to_seagate(grib_file, grib_dir, target_dir, feather_extension, feather_files)#, already_moved)

def move_file_to_seagate(grib_file, grib_dir, target_dir, feather_extension, feather_files):#, already_moved):
    if os.path.splitext(grib_file)[0] + feather_extension in feather_files:# and grib_file not in already_moved:
            source_path = os.path.join(grib_dir, grib_file)
            target_path = os.path.join(target_dir, grib_file)

            print(f"source_path: {source_path}, target_path: {target_path}")

            shutil.move(source_path, target_path)

            print(f"Moved: {source_path} to {target_path}")

def move_changed_CarraFeather_files(feather_dir: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/Feather', updated_dir: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/Feather/IndexUpdate/', backup_dir: str = 'D:/Skóli/lokaverkefni_vel/data/Carra/Feather/backup/'):
    updated = [file for file in os.listdir(updated_dir) if file.endswith('.feather')]

    for file in updated:
        shutil.move(os.path.join(feather_dir, file), os.path.join(backup_dir, file))
        shutil.move(os.path.join(updated_dir, file), os.path.join(feather_dir, file))   
        
#move_files_to_seagate("D:/Skóli/lokaverkefni_vel/data/Carra/GRIB", "D:/Skóli/lokaverkefni_vel/data/Carra/StrippedCarra", '.grib', '.feather', '/mnt/e/CopiedCarraGRIB')
            
move_changed_CarraFeather_files()