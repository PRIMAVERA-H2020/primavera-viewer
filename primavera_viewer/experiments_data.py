"""
Philip Rutter 11/07/18

Module defines classes for subsetting and averaging multi-model/ensemble
experiments as well as plotting functions to be used in the operation module.

"""

import iris
import numpy as np
from primavera_viewer import (nearest_location as loc, cube_format as format,
                              cube_plotting as cplot)


class ExperimentsData:
    """
    Class containing all experiment data and the requested location. Methods
    within class are used to manipulate spatial coordinates, time dimensions
    and cube formatting in order to accurately plot and compare experiments
    """
    def __init__(self, exp_list=iris.cube.CubeList([]), loc=np.array([])):
        self.experiments_list = exp_list
        self.location = loc

    def __repr__(self):
        if len(self.location) == 2:
            return '{experiments_list}\n' \
                   '{latitude}N {longitude}E'.format(
                experiments_list=self.experiments_list,
                latitude=self.location[0],
                longitude=self.location[1])
        if len(self.location) == 4:
            return '{experiments_list}\n{min_latitude}N to {max_latitude}N\n' \
                   '{min_longitude}E to {max_longitude}E'.format(
                experiments_list=self.experiments_list,
                min_latitude=self.location[0],
                max_latitude=self.location[1],
                min_longitude=self.location[2],
                max_longitude=self.location[3])

    def __str__(self):
        if len(self.location) == 2:
            return 'Experiments List:\n{experiments_list}\n' \
                   'Location:\n{latitude}N {longitude}E'.format(
                experiments_list=self.experiments_list,
                latitude=self.location[0],
                longitude=self.location[1])
        if len(self.location) == 4:
            return 'Experiments List:\n{experiments_list}\n' \
                   'Location:\nLatitude range: {min_latitude}N ' \
                   'to {max_latitude}N\n' \
                   'Longitude range: {min_longitude}E ' \
                   'to {max_longitude}E'.format(
                experiments_list=self.experiments_list,
                min_latitude=self.location[0],
                max_latitude=self.location[1],
                min_longitude=self.location[2],
                max_longitude=self.location[3])

    def unify_spatial_coordinates(self):
        """
        Ensure that all spatial dimensions are defined by the same coordinate
        system: two 1D arrays of latitude and longitude coordinates.
        Method for redefining spatial coordinates can be specific to each model.
        :return: ExperimentData class with unified spatial coords
        """
        all_cubes_list = iris.cube.CubeList([])
        for cube in self.experiments_list:
            cube = format.redefine_spatial_coords(cube)
            all_cubes_list.append(cube)
        self.experiments_list = all_cubes_list
        return self


    def constrain_location(self):
        """
        Purpose: Subsets cube location to set point in the coordinate system
        (CS). If self.location is a 2D array of latitude and longitude points a
        PointLocation class is created and the nearest known point in the CS is
        found. If self.location is a 4D array of min/max latitude and longitude
        points an AreaLocation class is created finding all nearest known points
        in the defined area and returning an area mean.
        :return: list of cubes at the requested point
        """
        if len(self.location) == 2:
            all_cubes_list = iris.cube.CubeList([])
            latitude_point = self.location[0]
            longitude_point = self.location[1]
            print('Constraining location at point:\n' + str(latitude_point) +
                  'N ' + str(longitude_point) + 'E')
            for cube in self.experiments_list:
                cube = loc.PointLocation(latitude_point, longitude_point, cube)
                cube = cube.find_point()
                all_cubes_list.append(cube)
            self.experiments_list = all_cubes_list
            return self
        if len(self.location) == 4:
            all_cubes_list = iris.cube.CubeList([])
            latitude_min = self.location[0]
            latitude_max = self.location[1]
            longitude_min = self.location[2]
            longitude_max = self.location[3]
            print('Constraining location over region:\n' 
                  'Latitude range: ' + str(latitude_min) + 'N to '
                  + str(latitude_max) + 'N\n'
                  'Longitude range: ' + str(longitude_min) + 'E to '
                  + str(longitude_max) + 'E')
            for cube in self.experiments_list:
                cube = loc.AreaLocation(latitude_min, latitude_max,
                                       longitude_min, longitude_max, cube)
                cube = cube.find_area()
                all_cubes_list.append(cube)
            self.experiments_list = all_cubes_list
            return self


    def unify_cube_format(self):
        """
        Ensure that all experiments have the same cube format i.e the same time
        coordinates and calendar, attributes, data type and auxillary coords.
        Time coordinate units and time point definitions can also be set.
        Example: units are set to be unified as 'days since 1950-01-01 00:00:00'
        and daily data is defined at the hour of midday.
        :return:
        """
        print('Unifying formatting')
        all_cubes_list = iris.cube.CubeList([])
        for cube in self.experiments_list:
            cube = format.change_calendar(cube,
                                          new_units='days since 1950-01-01 '
                                                    '00:00:00')
            cube = format.add_extra_time_coords(cube)
            cube = format.unify_data_type(cube)
            cube = format.set_blank_attributes(cube)
            cube = format.change_time_points(cube, hr=12)
            cube = format.change_time_bounds(cube)
            cube = format.remove_extra_time_coords(cube) # remove non-essential coord
            all_cubes_list.append(cube)
        self.experiments_list = all_cubes_list
        return self


class ExperimentsPlot:

    def __init__(self, exp_list=iris.cube.CubeList,
                 exp_mean=iris.cube.Cube, plot=''):
        self.experiments_list = exp_list
        self.experiments_mean = exp_mean
        self.plot_type = plot

    def plot_all(self):
        print('Starting plotting')
        if self.plot_type == 'annual_mean_timeseries':
            plot = cplot.annual_mean_timeseries(self.experiments_list,
                                                self.experiments_mean)
        if self.plot_type == 'experiments_mean_anomaly':
            plot = cplot.experiments_mean_anomaly(self.experiments_list,
                                                  self.experiments_mean)
        if self.plot_type == 'seasonal_mean_timeseries':
            plot = cplot.seasonal_mean_timeseries(self.experiments_list,
                                                  self.experiments_mean)
        if self.plot_type == 'monthly_anomaly_timeseries':
            plot = cplot.monthly_anomaly_timeseries(self.experiments_list)#,
                                                  #self.experiments_mean)
        return plot
