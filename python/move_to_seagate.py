import os
import shutil
from tqdm import tqdm

def move_files(grib_dir, feather_dir, grib_extension, feather_extension, target_dir):
    grib_files = [f for f in os.listdir(grib_dir) if f.endswith(grib_extension)]
    feather_files = [f for f in os.listdir(feather_dir) if f.endswith(feather_extension)]
    #already_moved = [f for f in os.listdir(target_dir) if f.endswith(grib_extension)]

    for grib_file in tqdm(grib_files, total = len(grib_files)):
        move_file(grib_file, grib_dir, target_dir, feather_extension, feather_files)#, already_moved)

def move_file(grib_file, grib_dir, target_dir, feather_extension, feather_files):#, already_moved):
    if os.path.splitext(grib_file)[0] + feather_extension in feather_files:# and grib_file not in already_moved:
            source_path = os.path.join(grib_dir, grib_file)
            target_path = os.path.join(target_dir, grib_file)

            print(f"source_path: {source_path}, target_path: {target_path}")

            shutil.move(source_path, target_path)

            print(f"Moved: {source_path} to {target_path}")

        
move_files("/mnt/d/skóli/lokaverkefni_vel/data/Carra/GRIB", "/mnt/d/skóli/lokaverkefni_vel/data/Carra/StrippedCarra", '.grib', '.feather', '/mnt/e/CopiedCarraGRIB')