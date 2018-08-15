"""
nearest_location.py
===================

Philip Rutter 15/08/18

Nearest known location module.

Creates a class defined by latitudes and a longitudes and a simulation that
finds the nearest known location in the given model and, if latitude and
longitude bounds are specified, defines the region to be averaged over for
location analysis.
"""

import iris

class PointLocation:
    """
    Class defined by a latitude point, a longitude point and a single cube
    constrained only in time from the simulations data set. These points are
    used as a reference to find the nearest known neighbour point within the
    cube model using 'find_point'.
    The result is a cube sub-setted at the nearest location to the input point.
    """

    def __init__(self, lat, lon, cube=iris.cube.Cube):
        """
        Initialise the class.

        :param float lat: Latitude point to constrain nearest known location to
        :param float lon: Longitude point to constrain nearest known location to
        :param iris.cube.Cube cube: A single cube from one simulation
        constrained only in time
        """
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
        """
        Rename the latitude coordinate of the input cube to the unified format
        required to merge all simulations and perform statistics
        """
        try:
            self.cube.coord('grid_latitude').rename('latitude')
        except:
            pass

    def rename_longitude(self):
        """
        Rename the longitude coordinate of the input cube to the unified format
        required to merge all simulations and perform statistics
        """
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
        """
        Based on the the input latitude/longitude point coordinate, finds the
        nearest neighbouring point int the specified cube's coordinate system.
        Function iterates through spatial coordinate bounds to find which bounds
        encompass the input point. The spatial coordinate associated with these
        bounds is assigned as the nearest known point.
        :return: The original cube sub-setted at the this nearest location point
        """
        lat_point = self.latitude    # define chosen latitude point from input
        lon_point = self.longitude   # define chosen longitude point from input
        self.rename_latitude()
        self.rename_longitude()
        all_lat_bounds = self.cube.coord('latitude').bounds
        all_lon_bounds = self.cube.coord('longitude').bounds
        # Iterate through each 2D array of the lower and upper bounds
        for i, lat_bounds in enumerate(all_lat_bounds):
            for j, lon_bounds in enumerate(all_lon_bounds):
                # Point must be smaller than max upper bound
                if lat_bounds[0] <= lat_point < lat_bounds[1]:
                    if lon_bounds[0] <= lon_point < lon_bounds[1]:
                        nlat = i
                        nlon = j
                    else:
                        pass
                else:
                    pass
                # Additional statements allowing points to match max upper bound
                if lat_point == all_lat_bounds[-1][1]:
                    nlat = i
                if lon_point == all_lon_bounds[-1][1]:
                    nlon = j
        return self.cube[:, nlat, nlon]

class AreaLocation:
    """
    Class defined by latitude minimum and maximum limits, longitude minimum and
    maximum limits and a single cube from the simulations data set constrained
    only in time.
    'find_area' finds the nearest neighbouring points of these limits within the
    cube's spatial coordinates, subsets all relevant data points and
    produces an area average of the region defined by the limits.
    """
    def __init__(self, lat_min, lat_max, lon_min, lon_max, cube=iris.cube.Cube):
        """
        Initialise the class.

        :param float lat_min: Minimum latitude boundary to constrain points to
        :param float lat_max: Maximum latitude boundary to constrain points to
        :param float lon_min: Minimum longitude boundary to constrain points to
        :param float lon_max: Maximum longitude boundary to constrain points to
        :param iris.cube.Cube cube: A single cube from one simulation
        constrained only in time
        """
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
        """
        Rename the latitude coordinate of the input cube to the unified format
        required to merge all simulations and perform statistics
        """
        try:
            self.cube.coord('grid_latitude').rename('latitude')
        except:
            pass

    def rename_longitude(self):
        """
        Rename the longitude coordinate of the input cube to the unified format
        required to merge all simulations and perform statistics
        """
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
        nearest known points for each limit point in the cube's coordinate
        system. The cube is subset with all points that lie within this bounded
        region and an area average is performed.
        The new cube's location is defined by the mean position
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
        # Iterate through each 2D array of the lower and upper bounds
        for i, lat_bounds in enumerate(all_lat_bounds):
            for j, lon_bounds in enumerate(all_lon_bounds):
                # Point must be smaller than max upper bound
                if lat_bounds[0] <= min_lat_point < lat_bounds[1]:
                    if lon_bounds[0] <= min_lon_point < lon_bounds[1]:
                        nlat_min = i
                        nlon_min = j
                    else:
                        pass
                else:
                    pass
                # Additional statements allowing points to match max upper bound
                if min_lat_point == all_lat_bounds[-1][1]:
                    nlat_min = i
                if min_lon_point == all_lon_bounds[-1][1]:
                    nlon_min = j
        # Iterate through each 2D array of the lower and upper bounds
        for k, lat_bounds in enumerate(all_lat_bounds):
            for l, lon_bounds in enumerate(all_lon_bounds):
                # Point must be smaller than max upper bound
                if lat_bounds[0] <= max_lat_point < lat_bounds[1]:
                    if lon_bounds[0] <= max_lon_point < lon_bounds[1]:
                        nlat_max = k
                        nlon_max = l
                    else:
                        pass
                else:
                    pass
                # Additional statements allowing points to match max upper bound
                if max_lat_point == all_lat_bounds[-1][1]:
                    nlat_max = i
                if max_lon_point == all_lon_bounds[-1][1]:
                    nlon_max = j
        area_subset = self.cube[:, nlat_min:nlat_max+1, nlon_min:nlon_max+1]
        area_mean = area_subset.collapsed(['latitude', 'longitude'],
                                          iris.analysis.MEAN)
        return area_mean