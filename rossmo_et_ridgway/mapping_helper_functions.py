import numpy as np

'''
This is used to convert latitude and longitude values to Web Mercator values for plotting purposes.
''' 

K = 6378137

def convert_longitude_to_webmercator(lon):
    return lon * (K * np.pi / 180.0)
    
def convert_latitude_to_webmercator(lat):
    return np.log(np.tan((90.0 + lat) * np.pi / 360.0)) * K