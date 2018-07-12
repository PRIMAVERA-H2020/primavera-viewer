"""
Philip Rutter 11/07/18

Module defines classes for subsetting and averaging multi-model/ensemble experiments as well as plotting functions to
be used in the operation module.

"""

import iris
import numpy as np
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from primavera_viewer import (singlecubestats as scs, nearestknownpoint as nkp)

class ExpStatistics:

    def __init__(self, exp_list=iris.cube.CubeList([]), loc=np.array([])):
        self.experiments_list = exp_list
        self.location = loc

    def constrain_location(self):
        """
        Purpose: Subsets cube location to set point in the coordinate system (CS). If self.location is a 2D array
        of latitude and longitude points a PointLocation class is created and the nearest known point in the CS is
        found. If self.location is a 4D array of min/max latitude and longitude points an AreaLocation class is created
        finding all nearest known points in the defined area and producing a zonal mean.
        :return: list of cubes at the requested point
        """
        if len(self.location) == 2:
            all_cubes_list = iris.cube.CubeList([])
            for cube in self.experiments_list:
                cube = nkp.PointLocation(self.location, cube)
                cube = cube.find_point()
                all_cubes_list.append(cube)
            return all_cubes_list
        if len(self.location) == 4:
            all_cubes_list = iris.cube.CubeList([])
            for cube in self.experiments_list:
                cube = nkp.AreaLocation(self.location, cube)
                cube = cube.find_area()
                all_cubes_list.append(cube)
            return all_cubes_list

    def all_experiments_mean(self):
        """
        Purpose: Calculates the multi-model/multi-ensemble mean for each time point for a given variable.
        :return: single cube containing multi-model/ensemble mean
        Note: All calendars are converted to a 360 day calendar by this script. Gregorian and 365 day calendars keep
        31/01 and 31/03 to balance 28/02. All other 31st days and leap days are removed.
        """
        all_cubes_list = iris.cube.CubeList([])
        for cube in self.experiments_list:
            cube = scs.change_cube_format(cube)
            all_cubes_list.append(cube)
        cubes = all_cubes_list
        merged_cube = cubes.merge_cube()
        experiments_mean = merged_cube.collapsed('experiment_label', iris.analysis.MEAN)

        return experiments_mean


class ExpPlotting:

    def __init__(self, exp_list=iris.cube.CubeList([]), exp_mean=iris.cube.Cube, plot=''):
        self.experiments_list = exp_list
        self.experiments_mean = exp_mean
        self.plot_type = plot

    def plot_all(self):
        ncubes = np.arange(0, len(self.experiments_list), 1)
        colours = ['r', 'b', 'g', 'c', 'm', 'y']
        if self.plot_type == 'annual mean timeseries':
            for n in ncubes:
                cube = self.experiments_list[n]
                cube = scs.change_cube_format(cube)
                cubes = scs.annual_mean(cube)
                cube_label = cubes[0].coord('experiment_label').points[0]
                qplt.plot(cubes[0], label=cube_label, color=colours[n])
                qplt.plot(cubes[1], linestyle='dashed', color=colours[n])
                qplt.plot(cubes[2], linestyle='dashed', color=colours[n])
            mean_cube = scs.annual_mean(self.experiments_mean)
            qplt.plot(mean_cube[0], label='experiment_mean', linestyle='dashed', color='black')
        plt.legend()
        plt.grid(True)
        plt.show()