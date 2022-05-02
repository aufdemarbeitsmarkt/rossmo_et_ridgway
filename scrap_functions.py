#!/usr/bin/python3

# a scrap-pile for functions I had in initial work for this project


def convert_latlon_to_webmercator(values, type='coordinates'):
    '''
    This is used to convert latitude and longitude values to Web Mercator values for plotting purposes.
    The default argument for type is 'coordinates'; this returns (lat, lon) coordinates converted to Web Mercator.
    When the type is 'range', the range of boundaries as given by get_area_of_interest_boundaries() is converted to Web Mercator and returned similar to the input tuple.
    '''
    k = 6378137

    def convert_longitude(longitude):
        webmercator_longitude = longitude * (k * np.pi / 180.0)
        return webmercator_longitude

    def convert_latitude(latitude):
        webmercator_latitude = np.log(np.tan((90.0 + latitude) * np.pi / 360.0)) * k
        return webmercator_latitude

    if type == 'coordinates':
        y = convert_latitude(values[0])
        x = convert_longitude(values[1])
        return x, y

    if type == 'range':
            y = tuple(convert_latitude(i) for i in values[0])
            x = tuple(convert_longitude(i) for i in values[1])
            return (x, y)
