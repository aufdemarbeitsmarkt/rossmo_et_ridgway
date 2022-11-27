from itertools import product
from typing import List, Type

from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure, output_file, output_notebook, show
from bokeh.tile_providers import CARTODBPOSITRON_RETINA, get_provider
from bokeh.transform import jitter
from geopy import units
from geopy.distance import geodesic
import numpy as np
from scipy.spatial import distance
import pandas as pd

from mapping_helper_functions import (convert_latitude_to_webmercator,
                                      convert_longitude_to_webmercator)


class Rossmo:

    default_accuracy = 500
    default_f = 1.0
    default_g = 1.0

    def __init__(
        self, 
        coordinates,
        f=None, 
        g=None,
        buffer=None,
        accuracy=None,
        max_distance=None
        ):

        self.coordinates = coordinates

        if f is None:
            f = self.default_f
        self.f = f
        
        if g is None:
            g = self.default_g
        self.g = g

        if buffer is None:
            buffer = self._get_buffer()
        self.buffer = buffer

        if accuracy is None:
            accuracy = self.default_accuracy
        self.accuracy = accuracy
        
        if max_distance is None:
            max_distance = self._get_max_distance()
        self.max_distance = max_distance

    @classmethod
    def from_dataframe(
        cls, 
        dataframe, 
        latitude_column='latitude', 
        longitude_column='longitude',
        **kwargs
        ):
        '''
        Creates an instance of Rossmo with a list of 1 or more dataframes. 
        '''

        if len(dataframe) > 1:
            df_output = pd.concat(dataframe)
        else: 
            df_output = dataframe[0]

        df_output['coordinates'] = list(zip(df_output[latitude_column], df_output[longitude_column]))        
        df_output['latitude_webmercator'] = convert_latitude_to_webmercator(df_output[latitude_column])
        df_output['longitude_webmercator'] = convert_longitude_to_webmercator(df_output[longitude_column])

        cls.df = df_output

        return cls(df_output['coordinates'].to_list(), **kwargs)

    @property
    def latitude(self):
        return [lat for lat,lon in self.coordinates]

    @property
    def longitude(self):
        return [lon for lat,lon in self.coordinates]
    
    def _get_max_distance(self):
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

    def _get_area_of_interest_boundaries(self):
        '''
        Returns min and max latitude and longitude boundaries for the area of interest.

        The area of interest taken by:
        - first getting the the min and max latitude and longitude for all crime locations, getting us the corresponding xs and ys for the northernmost, southernmost, easternmost, and westernmost points
        - then, we "fan" out from these by getting the max possible distance between all crime locations, _get_max_distance()

        This assumes that, for example:
        If the maximum distance between the list of all crime locations is 100 miles, then the criminal resides within 100 miles of the northernmost, southernmost, easternmost, or westernmost committed crime.

        69mi for 1º of lat from: https://www.thoughtco.com/degree-of-latitude-and-longitude-distance-4070616
        '''
        north, south, east, west = max(self.latitude), min(self.latitude), max(self.longitude), min(self.longitude)

        distance = self.max_distance
        one_latitude_degree_in_miles = 69

        latitude_min_max = (south - (distance / one_latitude_degree_in_miles), north + (distance / one_latitude_degree_in_miles))

        latitude_radians_min_max = (units.rad(degrees=l) for l in latitude_min_max)
        cosine_radians = (np.cos(l) for l in latitude_radians_min_max)
        one_longitude_degree_in_miles_min, one_longitude_degree_in_miles_max = (c * one_latitude_degree_in_miles for c in cosine_radians) # need two values -- one degree of longitude varies depending on latitude

        longitude_min_max = (east + (distance / one_longitude_degree_in_miles_min), west - (distance / one_longitude_degree_in_miles_max))

        self.area_of_interest_boundaries = boundaries = (latitude_min_max, longitude_min_max)

        return self.area_of_interest_boundaries

    def _get_area_of_interest(self):
        '''
        This uses the N, S, E, W boundaries provided by _get_area_of_interest_boundaries().

        Example: an accuracy of 500, gives us a granularity of ~1000ft (considering latitude). 
        '''
        latitude_min_max, longitude_min_max = self._get_area_of_interest_boundaries()
        latitude_range = np.linspace(latitude_min_max[0], latitude_min_max[1], num=self.accuracy)
        longitude_range = np.linspace(longitude_min_max[0], longitude_min_max[1], num=self.accuracy)

        area_of_interest = product(latitude_range,longitude_range)
        return area_of_interest

    def _get_buffer(self):
        manhattan = distance.cdist(self.coordinates, self.coordinates, metric='cityblock')
        buffer = np.min(manhattan[manhattan > 0])
        return buffer

    @property
    def rossmo_results(self):
        '''
        • lat, lon coordinates of crime (n in formula)
        • area_of_interest: lat, lon coordinates for which we're trying to get probabilty of residence
        • f & g: The main idea of the formula is that the probability of crimes first increases as one moves through the buffer zone away from the hotzone, but decreases afterwards. The variable f can be chosen so that it works best on data of past crimes. The same idea goes for the variable g.
        https://en.wikipedia.org/wiki/Rossmo%27s_formula#Explanation
        '''
        area_of_interest = list(self._get_area_of_interest())
        manhattan = distance.cdist(area_of_interest, self.coordinates, metric='cityblock')
        phi = manhattan > self.buffer

        rossmo_formula = (phi / abs(manhattan) ** self.f) + ((1 - phi) * (self.buffer ** (self.g - self.f)) / ((2 * self.buffer) - abs(manhattan)) ** self.g)

        rossmo_results_summed = np.sum(rossmo_formula, axis=1)

        return {k:v for k,v in zip(area_of_interest, rossmo_results_summed)}

    @property
    def df_rossmo_results(self): 
        # TODO: specify dtypes
        output_df = pd.DataFrame({'coordinates': self.rossmo_results.keys(), 'score': self.rossmo_results.values()})

        output_df[['latitude', 'longitude']] = pd.DataFrame(output_df['coordinates'].tolist(), index=output_df.index)
        output_df['score_normalized'] = (
            (output_df['score'] - output_df['score'].min()) / (output_df['score'].max() - output_df['score'].min())
            ) 
        return output_df


class RossmoPlot:

    def __init__(
        self, 
        rossmo_class: Type[Rossmo],
        plotting_dataframe: List[pd.DataFrame],
        set_score_array=None # manually define the score array, if desired; should probably make this a method 
        ):
        self.rossmo_class = rossmo_class
        self.df_rossmo_results = self.rossmo_class.df_rossmo_results # should I use inheritance here? simply assigning the variable here seems more straightforward, though
        self.plotting_dataframe = plotting_dataframe
        self.set_score_array = set_score_array

    def _check_update_coordinates_column(self):
        '''
        Check to ensure the plotting_dataframe has 'coordinates' column. If not, add it.
        '''
        for df in self.plotting_dataframe: 
            if 'coordinates' not in df.columns:
                df['coordinates'] = list(zip(df['latitude'], df['longitude']))

    def _set_below_percentile_to_zero(self, percentile='25%'):
        stats = self.df_rossmo_results['score'].describe()
        self.df_rossmo_results.loc[self.df_rossmo_results['score'] <= stats[percentile], ['score_normalized']] = 0.0

    def _convert_to_webmercator(self):
        self._check_update_coordinates_column()

        for df in [self.df_rossmo_results] + self.plotting_dataframe:
            df['latitude_webmercator'] = convert_latitude_to_webmercator(df['latitude'])
            df['longitude_webmercator'] = convert_longitude_to_webmercator(df['longitude'])

    @property
    def score_array(self):
        if self.set_score_array is None:
            return np.fliplr(
                self.df_rossmo_results['score_normalized']\
                .to_numpy()\
                .reshape((self.rossmo_class.accuracy, self.rossmo_class.accuracy))
            )
        else:
            return self.set_score_array

    @property
    def x_range(self):
        return self.df_rossmo_results['longitude_webmercator'].min(), self.df_rossmo_results['longitude_webmercator'].max()

    @property
    def y_range(self):
        return self.df_rossmo_results['latitude_webmercator'].min(), self.df_rossmo_results['latitude_webmercator'].max()

    def _prepare_plot(self):
        self._set_below_percentile_to_zero()
        self._convert_to_webmercator()

    def create_plot(
        self,
        legend_labels,
        fill_colors,
        plot_width=1080,
        plot_height=1080,
        tools=None,
        hover_details=None,
        heatmap_palette='Spectral10',
        heatmap_alpha=0.5,
        line_color='black',
        line_alpha=0.25,
        fill_alpha=0.6,
        radius=200
        ):
        self._prepare_plot()

        tile_provider = get_provider(CARTODBPOSITRON_RETINA)

        if hover_details is None:
            tooltips=[
                ('name', '@name'),
                ('coordinates', '@coordinates'),
                ('date', '@date'),
                ('notes', '@notes')
            ]
            hover = HoverTool(
                names=legend_labels,
                tooltips=tooltips
            )

        # generate a figure for the plot
        self.plot = figure(
            x_range=self.x_range,
            y_range=self.y_range,
            x_axis_type='mercator',
            y_axis_type='mercator',
            tools=['pan', 'wheel_zoom', 'save', 'reset', hover] if tools is None else tools,
            lod_threshold=None
        )

        # add the map tile
        self.plot.add_tile(tile_provider)

        # plot the heatmap (the rossmo results)
        self.plot.image(
            image=[self.score_array],
            x=self.x_range[0],
            y=self.y_range[0],
            dw=abs(self.x_range[1] - self.x_range[0]),
            dh=abs(self.y_range[1] - self.y_range[0]),
            palette=heatmap_palette,
            alpha=heatmap_alpha
        )

        # plot from the plotting dataframes
        for df, label, color in zip(self.plotting_dataframe, legend_labels, fill_colors):
            source = ColumnDataSource(df)
            self.plot.circle(
                x=jitter('longitude_webmercator', 0.05),
                y=jitter('latitude_webmercator', 0.05),
                radius=radius,
                fill_color=color,
                fill_alpha=fill_alpha,
                line_color=line_color,
                line_alpha=line_alpha,
                legend_label=label,
                source=source,
                name=label
            )
        
        # set legend policy
        self.plot.legend.click_policy='hide'

    def show_plot(self, output_to_notebook=True, output_html=False, html_filename=None, html_title=None):
        if output_to_notebook:
            output_notebook()
        if output_html:
            output_file(filename=f'maps/{html_filename}.html', title=html_title)
        show(self.plot)