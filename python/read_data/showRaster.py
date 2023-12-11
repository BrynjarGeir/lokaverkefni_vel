import rasterio
import lidario

path = '../data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif' #'../eco-sg_isl_v10_lzw.tif'

with rasterio.open(path) as dataset:
    crs = dataset.crs
    transform = dataset.transform

    descriptions = dataset.descriptions

    elevation = dataset.read(1)

    width, height = elevation.shape

    x1,y1 = transform * (0, 0)
    x2, y2 = transform * (height-1,  width - 1)

    print(f"Coordinates: ({x1}, {y1}) for first point")
    print(f"Coordinates: ({x2}, {y2}) for last point")
    print(transform)


    exit()
    for row in range(height-1, height-10, -1):#height):
        for col in range(width-1, width-10, -1):#width):
            col = 10000
            x, y = transform * (col, row)
            z = elevation[col, row]

            print(f"Coordinates: ({x}, {y}), Elevation: {z}")

#import numpy as np

# Open the dataset
#with rasterio.open(path) as src:
    # Read a specific band (e.g., band 1)
    #band = src.read(1)

    # Use NumPy to calculate the unique values and their counts
    #unique_values, counts = np.unique(band, return_counts=True)

    # Calculate the total number of pixels
    #total_pixels = band.size

    # Calculate the percentage of each unique value
    #percentages = (counts / total_pixels) * 100

    # Create a dictionary to store value-count pairs
    #value_counts = dict(zip(unique_values, counts))

    # Print or access the distribution, e.g., percentage of pixels with value 1
    #print("Distribution of unique values:")
    #for value, percentage in zip(unique_values, percentages):
    #    print(f"Value {value}: {percentage:.2f}%")

    # Access count of pixels with a specific value, e.g., value 1
    #count_of_value_1 = value_counts.get(1, 0)
    #print(f"Count of pixels with value 1: {count_of_value_1}")
