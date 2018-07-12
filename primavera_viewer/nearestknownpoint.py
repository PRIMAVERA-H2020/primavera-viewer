

"""
Philip Rutter 26/06/18

Nearest Known Point module

Creates a class defined by a latitude and a longitude and an experiment that finds the nearest known
point in the given model and/or defines a region to be averaged over for location analysis.

"""

import numpy as np
import iris

class PointLocation:

    def __init__(self, p=np.array([0, 0]), cube=iris.cube.Cube(0.0)):
        self.point = p
        self.singlecube = cube

    def setpoint(self, p):
        self.point = p

    def setsinglecube(self, cube):
        self.singlecube = cube

    def __repr__(self):
        return "%s(p=%s, cube=%s)" % ("PointLocation", self.point, self.singlecube)

    def __str__(self):
        return "(%s, %s, %s)" % (self.point[0], self.point[1], self.singlecube)

    def find_point(self):
        lat_point = self.point[0]    # define chosen latitude point from input
        lon_point = self.point[1]    # define chosen longitude point from input

        cube_lat = self.singlecube.coord('latitude')
        cube_lon = self.singlecube.coord('longitude')
        all_lat_bounds = cube_lat.bounds   # create array of all latitude bounds for input cube (model specific)
        all_lon_bounds = cube_lon.bounds  # create array of all longitude bounds for input cube (model specific)
        nlat_arr = np.arange(0, len(all_lat_bounds), 1)
        nlon_arr = np.arange(0, len(all_lon_bounds), 1)

        for lat in nlat_arr:
            for lon in nlon_arr:
                lat_bounds = all_lat_bounds[lat]    # 2D array of the lower and upper lat bounds
                lon_bounds = all_lon_bounds[lon]    # 2D array of the lower and upper lon bounds
                if lat_point >= lat_bounds[0] and lat_point < lat_bounds[1]:
                    if lon_point >= lon_bounds[0] and lon_point < lon_bounds[1]:
                        return self.singlecube[:, lat, lon]
                    else:
                        pass
                else:
                    pass

class AreaLocation:

    def __init__(self, a=np.array([0, 0, 0, 0]), cube=iris.cube.Cube(0.0)):
        self.area = a
        self.singlecube = cube

    def setarea(self, a):
        self.area = a

    def setsinglecube(self, cube):
        self.singlecube = cube

    def __repr__(self):
        return "%s(a=%s, cube=%s)" % ("AreaLocation", self.area, self.singlecube)

    def __str__(self):
        return "(%s, %s, %s, %s, %s)" % (self.area[0], self.area[1], self.area[2],
                                         self.area[3], self.singlecube)

    def find_area(self):
        minlat_point = self.area[0]
        maxlat_point = self.area[1]
        minlon_point = self.area[2]
        maxlon_point = self.area[3]

        cube_lat = self.singlecube.coord('latitude')
        cube_lon = self.singlecube.coord('longitude')
        all_lat_bounds = cube_lat.bounds   # create array of all latitude bounds for input cube (model specific)
        all_lon_bounds = cube_lon.bounds  # create array of all longitude bounds for input cube (model specific)
        nlat_arr = np.arange(0, len(all_lat_bounds), 1)
        nlon_arr = np.arange(0, len(all_lon_bounds), 1)

        for lat in nlat_arr:
            for lon in nlon_arr:
                lat_bounds = all_lat_bounds[lat]    # 2D array of the lower and upper lat bounds
                lon_bounds = all_lon_bounds[lon]    # 2D array of the lower and upper lon bounds
                if minlat_point >= lat_bounds[0] and minlat_point < lat_bounds[1]:
                    if minlon_point >= lon_bounds[0] and minlon_point < lon_bounds[1]:
                        lat_min = lat
                        lon_min = lon
                    else:
                        pass
                else:
                    pass

        for lat in nlat_arr:
            for lon in nlon_arr:
                lat_bounds = all_lat_bounds[lat]    # 2D array of the lower and upper lat bounds
                lon_bounds = all_lon_bounds[lon]    # 2D array of the lower and upper lon bounds
                if maxlat_point >= lat_bounds[0] and maxlat_point < lat_bounds[1]:
                    if maxlon_point >= lon_bounds[0] and maxlon_point < lon_bounds[1]:
                        lat_max = lat
                        lon_max = lon
                    else:
                        pass
                else:
                    pass

        area_subset = self.singlecube[:, lat_min:lat_max, lon_min:lon_max]

        area_mean = area_subset.collapsed(['latitude', 'longitude'], iris.analysis.MEAN)

        return area_mean