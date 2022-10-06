#!/usr/bin/python3
import numpy as np

latitudes = np.random.uniform(low=46.000, high=47.000, size=25)
longitudes = np.random.uniform(low=121.000, high=122.000, size=25)
coordinates = list(zip(latitudes, longitudes))
