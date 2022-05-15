#!/usr/bin/python3
from geopy.distance import geodesic
from geopy import units
from itertools import product
import numpy as np
import pandas as pd
from scipy.spatial import distance


class Rossmo:

    default_accuracy = 500

    def __init__(self, coordinates, accuracy=None, max_distance=None):
        self.coordinates = coordinates
        self.latitudes = [lat for lat,lon in self.coordinates]
        self.longitudes = [lon for lat,lon in self.coordinates]

        if accuracy is None:
            accuracy = self.default_accuracy
        self.accuracy = accuracy
        
        if max_distance is None:
            max_distance = self.get_max_distance()
        self.max_distance = max_distance
        
        self.rossmo_formula = self.rossmo_formula()

        # consider adding f and g in rossmo_formula() as kwargs
    
    def get_max_distance(self):
        '''
        Returns the maximum distance for all crime locations; argument should be the cartesian product of all combinations of locations, derived from get_cartesian_product_of_locations().

         # possibly use scipy.distance.cdist instead.
        '''
        cartesian_product_of_coordinates = product(self.coordinates, repeat=2)
        distances = []
        for l1,l2 in cartesian_product_of_coordinates:
            distances.append(geodesic(l1, l2).miles)
        max_distance = max(distances)
        return max_distance

    def get_area_of_interest_boundaries(self):
        '''
        Returns min and max latitude and longitude boundaries for the area of interest.

        The area of interest taken by:
        - first getting the the min and max latitudes and longitudes for all crime locations, getting us the corresponding xs and ys for the northernmost, southernmost, easternmost, and westernmost points
        - then, we "fan" out from these by getting the max possible distance between all crime locations, get_max_distance()

        This assumes that, for example:
        If the maximum distance between the list of all crime locations is 100 miles, then the criminal resides within 100 miles of the northernmost, southernmost, easternmost, or westernmost committed crime.

        69mi for 1º of lat from: https://www.thoughtco.com/degree-of-latitude-and-longitude-distance-4070616
        '''
        north, south, east, west = max(self.latitudes), min(self.latitudes), max(self.longitudes), min(self.longitudes)

        distance = self.max_distance
        one_latitude_degree_in_miles = 69

        latitude_min_max = (south - (distance / one_latitude_degree_in_miles), north + (distance / one_latitude_degree_in_miles))

        latitude_radians_min_max = (units.rad(degrees=l) for l in latitude_min_max)
        cosine_radians = (np.cos(l) for l in latitude_radians_min_max)
        one_longitude_degree_in_miles_min, one_longitude_degree_in_miles_max = (c * one_latitude_degree_in_miles for c in cosine_radians) # need two values -- one degree of longitude varies depending on latitude

        longitude_min_max = (east + (distance / one_longitude_degree_in_miles_min), west - (distance / one_longitude_degree_in_miles_max))

        boundaries = (latitude_min_max, longitude_min_max)

        return boundaries

    def get_area_of_interest(self):
        '''
        This uses the N, S, E, W boundaries provided by get_area_of_interest_boundaries().

        Right now, an accuracy of 500, which would be np.linspace(start,stop,num=500), should give us accuracy of ~1000ft. (considering latitude). For the purposes of getting this working, this should be sufficient.

        Thought: Am I overcomplicating this by using a max_distance in miles?
        '''
        latitude_min_max, longitude_min_max = self.get_area_of_interest_boundaries()
        latitude_range = np.linspace(latitude_min_max[0], latitude_min_max[1], num=self.accuracy)
        longitude_range = np.linspace(longitude_min_max[0], longitude_min_max[1], num=self.accuracy)

        area_of_interest = product(latitude_range,longitude_range)

        return area_of_interest

    def get_buffer(self):
        '''
        Latitude is the Y axis.
        Longitude is the X axis.
        '''
        manhattan = distance.cdist(self.coordinates, self.coordinates, metric='cityblock')
        buffer = np.median(manhattan)
        return buffer

    def get_phi(self, manhattan_distance, buffer):
        return 1 if manhattan_distance > buffer else 0

    def rossmo_formula(self, f=0.5, g=1):
        '''
        • lat, lon coordinates of crime (n in formula)
        • area_of_interest: lat, lon coordinates for which we're trying to get probabilty of residence
        • f & g: The main idea of the formula is that the probability of crimes first increases as one moves through the buffer zone away from the hotzone, but decreases afterwards. The variable f can be chosen so that it works best on data of past crimes. The same idea goes for the variable g.
        '''
        area_of_interest = self.get_area_of_interest()
        rossmo = {}
        B = self.get_buffer()
        p = 0
        for a,i in area_of_interest:
            for lat, lon in self.coordinates:
                manhattan = distance.cityblock([a,i],[lat, lon])
                phi = self.get_phi(manhattan_distance=manhattan, buffer=B)
                p += (phi / abs(manhattan) ** f) + ((1 - phi) * (B ** (g - f)) / ((2 * B) - abs(manhattan)) ** g)
            rossmo[(a,i)] = p
            p = 0
        return rossmo
