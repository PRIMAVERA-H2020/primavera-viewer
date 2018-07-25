

"""
Philip Rutter 26/06/18

Nearest Known Point module

Creates a class defined by a latitude and a longitude and an experiment that
finds the nearest known point in the given model and/or defines a region to be
averaged over for location analysis.

"""

import numpy as np
import iris
from primavera_viewer import exp_format as format

class PointLocation:

    def __init__(self, lat, lon, cube=iris.cube.Cube):
        self.latitude = lat
        self.longitude = lon
        self.cube = cube

    def set_latitude(self, lat):
        self.latitude = lat

    def set_longitude(self, lon):
        self.longitude = lon

    def set_cube(self, cube):
        self.cube = cube

    def rename_latitude(self):
        try:
            self.cube.coord('grid_latitude').rename('latitude')
        except:
            pass

    def rename_longitude(self):
        try:
            self.cube.coord('grid_longitude').rename('longitude')
        except:
            pass

    def __repr__(self):
        return "PointLocation: {latitude}, {longitude}, {cube}".format(
            latitude=self.latitude, longitude=self.longitude, cube=self.cube)

    def __str__(self):
        return "{latitude}, {longitude}, {cube}".format(
            latitude=self.latitude, longitude=self.longitude, cube=self.cube)

    def find_point(self):
        lat_point = self.latitude    # define chosen latitude point from input
        lon_point = self.longitude   # define chosen longitude point from input
        self.rename_latitude()
        self.rename_longitude()
        all_lat_bounds = self.cube.coord('latitude').bounds
        all_lon_bounds = self.cube.coord('longitude').bounds
        for i, lat in enumerate(all_lat_bounds):
            for j, lon in enumerate(all_lon_bounds):
                lat_bounds = lat    # 2D array of the lower and upper lat bounds
                lon_bounds = lon    # 2D array of the lower and upper lon bounds
                if lat_bounds[0] <= lat_point < lat_bounds[1]:
                    if lon_bounds[0] <= lon_point < lon_bounds[1]:
                        return self.cube[:, i, j]
                    else:
                        pass
                else:
                    pass

class AreaLocation:

    def __init__(self, lat_min, lat_max, lon_min, lon_max, cube=iris.cube.Cube):
        self.latitude_min = lat_min
        self.latitude_max = lat_max
        self.longitude_min = lon_min
        self.longitude_max = lon_max
        self.cube = cube

    def set_lat_min(self, lat_min):
        self.latitude_min = lat_min

    def set_lat_max(self, lat_max):
        self.latitude_max = lat_max

    def set_lon_min(self, lon_min):
        self.longitude_min = lon_min

    def set_lon_max(self, lon_max):
        self.longitude_max = lon_max

    def set_cube(self, cube):
        self.cube = cube

    def rename_latitude(self):
        try:
            self.cube.coord('grid_latitude').rename('latitude')
        except:
            pass

    def rename_longitude(self):
        try:
            self.cube.coord('grid_longitude').rename('longitude')
        except:
            pass

    def __repr__(self):
        return "AreaLocation: {latitude_min}, {latitude_max}, " \
               "{longitude_min}, {longitude_max}, {cube}".format(
            latitude_min=self.latitude_min, latitude_max=self.latitude_max,
            longitude_min=self.longitude_min, longitude_max=self.longitude_max,
            cube=self.cube)

    def __str__(self):
        return "{latitude_min}, {latitude_max}, {longitude_min}, " \
               "{longitude_max}, {cube}".format(
            latitude_min=self.latitude_min, latitude_max=self.latitude_max,
            longitude_min=self.longitude_min, longitude_max=self.longitude_max,
            cube=self.cube)

    def find_area(self):
        """
        Finds an area averaged cube based on latitude and longitude min/max
        boundaries. With boundaries defined, the function first finds the
        nearest known points in the cube's coordinate system and returns an area
        averaged cube. The new cube's location is defined by the mean position
        of nearest known points NOT the mean position of the input boundaries.
        """
        min_lat_point = self.latitude_min
        max_lat_point = self.latitude_max
        min_lon_point = self.longitude_min
        max_lon_point = self.longitude_max
        self.rename_latitude()
        self.rename_longitude()
        all_lat_bounds = self.cube.coord('latitude').bounds
        all_lon_bounds = self.cube.coord('longitude').bounds
        # print(all_lat_bounds)
        # print(all_lon_bounds)
        for i, lat in enumerate(all_lat_bounds):
            for j, lon in enumerate(all_lon_bounds):
                lat_bounds = lat    # 2D array of the lower and upper lat bounds
                lon_bounds = lon    # 2D array of the lower and upper lon bounds
                if lat_bounds[0] <= min_lat_point < lat_bounds[1]:
                    if lon_bounds[0] <= min_lon_point < lon_bounds[1]:
                        nlat_min = i
                        nlon_min = j
                    else:
                        pass
                else:
                    pass

        for k, lat in enumerate(all_lat_bounds):
            for l, lon in enumerate(all_lon_bounds):
                lat_bounds = lat    # 2D array of the lower and upper lat bounds
                lon_bounds = lon    # 2D array of the lower and upper lon bounds
                if lat_bounds[0] <= max_lat_point < lat_bounds[1]:
                    if lon_bounds[0] <= max_lon_point < lon_bounds[1]:
                        nlat_max = k
                        nlon_max = l
                    else:
                        pass
                else:
                    pass

        area_subset = self.cube[:, nlat_min:nlat_max+1, nlon_min:nlon_max+1]
        # print(area_subset.coord('latitude').points)
        # print(area_subset.coord('longitude').points)
        area_mean = area_subset.collapsed(['latitude', 'longitude'],
                                          iris.analysis.MEAN)

        return area_mean