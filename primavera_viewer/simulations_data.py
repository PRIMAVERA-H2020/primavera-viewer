"""
simulations_data.py
===================

Philip Rutter 14/08/18

Module defines a class 'SimulationsData' used to manipulating and handling data
from simulations once fully loaded and concatenated.
"""
import logging
from multiprocessing import Process, Manager
import itertools
import cf_units
import iris
import numpy as np
from primavera_viewer import (nearest_location as loc, sim_format as format)
from datetime import datetime

logger = logging.getLogger(__name__)

class SimulationsData:
    """
    Class containing all simulation data and the requested location. Methods
    within class are used to manipulate spatial coordinates, time dimensions
    and cube formatting in order to accurately plot and compare simulations.

    Note: All calendars are converted to a 360 day calendar by this script.
    Gregorian and 365 day calendars keep 31/01 and 31/03 to balance 28/02.
    All other 31st days and leap days are removed.

    Example:
    SimulationsData(sim_list = a_raw_cube_list
                    loc = [30.2, 45.7], # or [30.2, 34.3, 45.7, 48.5] for area
                    t_constr = [1950, 2010])
    """
    def __init__(self, sim_list=iris.cube.CubeList([]), loc=([]),
                 t_constr=([])):
        """
        Initialise the class.

        :param iris.cube.CubeList sim_list: Cube list containing concatenated
        lazy data for each simulation
        :param array loc: An array to be used for constraining at location
        (a two element array for a point or four element array for regional
        boundaries)
        :param array t_constr: A two element array for specifying start and
        end year of data
        """
        self.simulations_list = sim_list
        self.location = loc
        self.time_constraints = t_constr

    def __repr__(self):
        if len(self.location) == 2:
            return '{simulations_list}\n' \
                   '{latitude}N {longitude}E'.format(
                simulations_list=self.simulations_list,
                latitude=self.location[0],
                longitude=self.location[1])
        if len(self.location) == 4:
            return '{simulations_list}\n{min_latitude}N to {max_latitude}N\n' \
                   '{min_longitude}E to {max_longitude}E'.format(
                simulations_list=self.simulations_list,
                min_latitude=self.location[0],
                max_latitude=self.location[1],
                min_longitude=self.location[2],
                max_longitude=self.location[3])

    def __str__(self):
        if len(self.location) == 2:
            return 'Simulations List:\n{simulations_list}\n' \
                   'Location:\n{latitude}N {longitude}E'.format(
                simulations_list=self.simulations_list,
                latitude=self.location[0],
                longitude=self.location[1])
        if len(self.location) == 4:
            return 'Simulations List:\n{simulations_list}\n' \
                   'Location:\nLatitude range: {min_latitude}N ' \
                   'to {max_latitude}N\n' \
                   'Longitude range: {min_longitude}E ' \
                   'to {max_longitude}E'.format(
                simulations_list=self.simulations_list,
                min_latitude=self.location[0],
                max_latitude=self.location[1],
                min_longitude=self.location[2],
                max_longitude=self.location[3])

    def unify_spatial_coordinates(self, params, output):
        """
        Ensures that all spatial dimensions are defined by the same coordinate
        system: two 1D arrays of latitude and longitude coordinates.
        Method for redefining spatial coordinates can be specific to each model.

        :param iris.cube.Cube params: Cube to spatially unify
        :param iris.cube.CubeList output: Cube list to contain spatially unified
         cubes
        :return iris.cube.Cube: Spatially unified cube
        """
        cube = params.get()
        cube = format.redefine_spatial_coords(cube)
        output.append(cube)

    def constrain_location(self, params, output):
        """
        Subsets cube location to single point in the coordinate system (CS). If
        self.location is a 2D array of latitude and longitude points a
        PointLocation class is created and the nearest known point in the CS is
        found. If self.location is a 4D array of min/max latitude and longitude
        points an AreaLocation class is created finding all nearest known points
        in the defined area and returning an area mean.

        :param iris.cube.Cube params: Cube to constrain at location
        :param iris.cube.CubeList output: Cube list to contain constrained cubes
        :return iris.cube.Cube: Constrained cube
        """
        cube = params.get()
        if len(self.location) == 2:
            latitude_point = self.location[0]
            longitude_point = self.location[1]
            logger.debug('Constraining location for '
                         +cube.coord('simulation_label').points[0]+
                         ' at point:\n'+str(latitude_point)+'N '+
                         str(longitude_point)+'E')
            cube = loc.PointLocation(latitude_point, longitude_point, cube)
            cube = cube.find_point()
            output.append(cube)
        if len(self.location) == 4:
            latitude_min = self.location[0]
            latitude_max = self.location[1]
            longitude_min = self.location[2]
            longitude_max = self.location[3]
            logger.debug('Constraining location for '+
                         cube.coord('simulation_label').points[0]+
                         ' over region:\nLatitude range: '+str(latitude_min)+
                         'N to '+str(latitude_max)+'N\nLongitude range: '+
                         str(longitude_min)+'E to '+str(longitude_max)+'E')
            cube = loc.AreaLocation(latitude_min, latitude_max,
                                       longitude_min, longitude_max, cube)
            cube = cube.find_area()
            output.append(cube)

    def unify_cube_format(self, params, output, time_constr):
        """
        Ensure that all simulations have the same cube format i.e the same time
        coordinates and calendar, attributes, data type and auxillary coords.
        Time coordinate units and time point definitions can also be set.
        Example: units are currently set to be unified as
        'days since 1950-01-01 00:00:00' and daily data is defined at the hour
        of midday.

        :param iris.cube.Cube params: Cube to reformat
        :param iris.cube.CubeList output: Cube list to contain reformatted cubes
        :param np.array t_constr: A two element array for specifying start and
        end year of data
        :return iris.cube.Cube: Reformatted cube
        """
        cube=params.get()
        logger.debug('Unifying formatting for '
                     +cube.coord('simulation_label').points[0])
        cube = format.change_calendar(cube, time_constr,
                                      new_units='days since 1950-01-01 '
                                                '00:00:00')
        cube = format.add_extra_time_coords(cube)
        cube = format.unify_data_type(cube)
        cube = format.set_blank_attributes(cube)
        cube = format.change_time_points(cube, hr=12) # daily data = midday
        cube = format.change_time_bounds(cube)
        cube = format.remove_extra_time_coords(cube)# remove non-essential coord
        output.append(cube)

    def mask_bad_data(self, params, output):
        """
        If bad points are known to exist in a dataset then these are masked.

        :param iris.cube.Cube params: Cube to reformat
        :param iris.cube.CubeList output: Cube list to contain reformatted cubes
        :param np.array t_constr: A two element array for specifying start and
        end year of data
        :return iris.cube.Cube: Reformatted cube
        """
        cube=params.get()

        simulation_label = cube.coord('simulation_label').points[0]

        if 'CMCC-CM2-VHR4' in simulation_label:
            dt = datetime(2003, 2, 2, 12, 0, 0)
            tc = cube.coord('time')
            numeric_date = cf_units.date2num(dt, tc.units.name,
                                             tc.units.calendar)
            time_point_array = np.where(tc.points==numeric_date)[0]
            if len(time_point_array) == 0:
                logger.warning('Cannot mask. {} not found in {}'.
                               format(dt, simulation_label))
            else:
                time_point_index = time_point_array[0]
                cube.data[time_point_index, ...] = np.ma.masked
                logger.debug('Masking bad data for {} at {}'.
                             format(simulation_label, dt))
        else:
            logger.debug('No data requires masking for {}'.format
                         (simulation_label))
        output.append(cube)

    def simulations_operations(self):
        """
        Perform all the above operations in parallel for each simulation the
        user wishes to compare.

        :return self: self.simulations_list refactored as the unified cube list
        """
        operations = ['unifying spatial coords', 'constraining location',
                      'unifying cube format', 'mask_bad_data']
        for oper in operations:
            jobs = []
            manager = Manager()
            params = manager.Queue()
            result_list = manager.list()
            if oper == 'unifying spatial coords':
                func = self.unify_spatial_coordinates
                arguments = (params, result_list)
            if oper == 'constraining location':
                func = self.constrain_location
                arguments = (params, result_list)
            if oper == 'unifying cube format':
                func = self.unify_cube_format
                arguments = (params, result_list, self.time_constraints)
            if oper == 'mask_bad_data':
                func = self.mask_bad_data
                arguments = (params, result_list)
            max_simul_jobs = len(self.simulations_list)
            for i in range(max_simul_jobs):
                p = Process(target=func, args=arguments)
                jobs.append(p)
                p.start()
            iters = itertools.chain(
                self.simulations_list,(None,) * max_simul_jobs)
            for iter in iters:
                params.put(iter)
            for j in jobs:
                   j.join()
            self.simulations_list = iris.cube.CubeList(list(result_list))
        return self


    def all_simulations_mean(self):
        """
        Calculates the multi-simulation mean from the cube list of fully unified
        simulations data above.

        :return iris.cube.Cube simulations_mean: A single iris cube calculated
        from the mean of all the cube simulations at each time point
        """
        if len(self.simulations_list) > 1:
            sttime = datetime.now()
            all_cubes_list = iris.cube.CubeList([])
            for cube in self.simulations_list:
                try:
                    cube.remove_coord('latitude')
                except:
                    pass
                try:
                    cube.remove_coord('longitude')
                except:
                    pass
                all_cubes_list.append(cube)
            cubes = all_cubes_list
            merged_cube = cubes.merge_cube()
            simulations_mean = merged_cube.collapsed('simulation_label',
                                                     iris.analysis.MEAN)
            simulations_mean.coord(
                'simulation_label').points[0]='Simulations Mean'
            entime = datetime.now()
            logger.debug('Time ellapsed when calculating mean: '+
                         str(entime-sttime))
            return simulations_mean
        else:
            return iris.cube.Cube([])