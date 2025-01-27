import os
import zipfile
import xarray as xr

def extract_nc_files(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

def merge_nc_files(nc_files):
    datasets = [xr.open_dataset(nc_file) for nc_file in nc_files]
    merged_dataset = xr.concat(datasets, dim='time')
    return merged_dataset

def main():
    icel_folder = 'icel'
    temp_extract_folder = 'temp_extract'
    os.makedirs(temp_extract_folder, exist_ok=True)
    
    nc_files = []
    
    for root, dirs, files in os.walk(icel_folder):
        for file in files:
            if file.endswith('.nc'):
                file_path = os.path.join(root, file)
                if zipfile.is_zipfile(file_path):
                    extract_nc_files(file_path, temp_extract_folder)
                    for extracted_file in os.listdir(temp_extract_folder):
                        if extracted_file.endswith('.nc'):
                            nc_files.append(os.path.join(temp_extract_folder, extracted_file))
                else:
                    nc_files.append(file_path)
    
    if 'data_0.nc' in nc_files and 'data_1.nc' in nc_files:
        data_0_path = os.path.join(icel_folder, 'data_0.nc')
        data_1_path = os.path.join(icel_folder, 'data_1.nc')
        merged_data = merge_nc_files([data_0_path, data_1_path])
        merged_data.to_netcdf(os.path.join(icel_folder, 'merged_data.nc'))
    
    if nc_files:
        merged_dataset = merge_nc_files(nc_files)
        merged_dataset.to_netcdf(os.path.join(icel_folder, 'all_merged_data.nc'))
    
    # Clean up temporary extraction folder
    for file in os.listdir(temp_extract_folder):
        os.remove(os.path.join(temp_extract_folder, file))
    os.rmdir(temp_extract_folder)

if __name__ == "__main__":
    main()