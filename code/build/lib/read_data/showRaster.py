import rasterio
import dill as pickle
from getPickledObjects import Affine
path = "D:Skóli/lokaverkefni_vel/data/elevationPoints/pointDist/884-1391.pkl"
path = '../data/elevationPoints/IslandsDEMv1.0_20x20m_isn93_zmasl.tif' #'../eco-sg_isl_v10_lzw.tif'

with rasterio.open(path) as dataset:
    crs = dataset.crs
    transform = dataset.transform
    index = dataset.index

outputPath = 'D:Skóli/lokaverkefni_vel/data/elevationPoints/transform.pkl'



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
