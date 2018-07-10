"""
Philip Rutter 02/07/18

Module for constrained loading and concatenation of data from either a single ensemble member or multiple ensembles to
be compared.

"""

import os
import iris
import numpy as np
import iris.coord_categorisation as icc


class Experiments:
    """
    A class of experiments with data that can be loaded individually concatenated and combined into a cube list for
    multiple models, ensembles and versions at varying resolutions for a single variable
    """
    def __init__(self, var=list(), mod=list(), ens=list(), ver=list()):
        self.variables = var
        self.models = mod
        self.ensembles = ens
        self.versions = ver

    def set_variables(self, var):
        self.variables = var

    def set_models(self, mod):
        self.models = mod

    def set_ensembles(self, ens):
        self.ensembles = ens

    def set_versions(self, ver):
        self.versions = ver

    def __repr__(self):
        return "%s(var=%s, mod=%s, ens=%s, ver=%s)" % \
               ("Multi Simulation", self.variables, self.models, self.ensembles, self.versions)

    def __str__(self):
        return "(%s, %s, %s, %s)" % (self.variables, self.models, self.ensembles, self.versions)

    def load_data(self, model='', ensemble='', variable='', version='', input_constraints=np.array([[], [], []])):
        """
        Loads data with defined constraints on time (year), latitude and longitude for single experiment.
        Concludes whether data exists.
        Returns cube list
        """
        def my_callback(cube, field, filename):
            # add a categorical year coordinate to the cube
            icc.add_year(cube, 'time')

        year_arr = range(input_constraints[0][0], input_constraints[0][1], 1)

        constraints = iris.Constraint(year=lambda y: y in year_arr)#,
        #                               latitude=lambda lat: input_constraints[1][0] <= lat <= input_constraints[1][1],
        #                               longitude=lambda lon: input_constraints[2][0] <= lon <= input_constraints[2][1])

        topdir = '/scratch/jseddon/primavera/stream1'   # top level data directory
        datadir = '/CMIP6/HighResMIP/' + model + '/highresSST-present/' + ensemble \
                  + '/day/' + variable + '/' + version + '/'
        dir = topdir + datadir

        if os.path.isdir(dir) == True:
            print('Loading ' + variable + ' data for model ensemble ' + model + ' ' + ensemble + ' at resolution '
                  + version)
            return iris.load(dir + '*.nc', constraints, callback=my_callback)
        else:
            print('File for ' + variable + ' data for model ensemble ' + model + ' ' + ensemble + ' at resolution '
                  + version + ' does not exist')


    def concatenate_data(self, cubes=iris.cube.CubeList([])):
        """
        Concatenates data cubes for all experiments

        """
        attributes = ['creation_date', 'history', 'tracking_id']
        for cube in cubes:
            for attr in attributes:
                cube.attributes[
                    attr] = ''
        return cubes.concatenate_cube()

    def load_all_data(self, concatenate=None, input_constraints=np.array([[], [], []])):
        """
        Loads data for multiple experiments based on constraints for time (year), latitude and longitude.
        Option to concatenate experiment cubes if required
        returns a cube list

        """
        all_cube_list = iris.cube.CubeList([])
        conc_cube_list = iris.cube.CubeList([])

        for v in self.variables:
            for m in self.models:
                for e in self.ensembles:
                    for vr in self.versions:
                        model = str(m)
                        ensemble = str(e)
                        variable = str(v)
                        version= str(vr)
                        cubes = self.load_data(model, ensemble, variable, version, input_constraints)
                        if cubes == None:
                            pass
                        else:
                            if concatenate is not None:
                                conc_cube = self.concatenate_data(cubes)
                                conc_cube_list.append(conc_cube)
                                cube_list = conc_cube_list
                            else:
                                for cube in cubes:
                                    all_cube_list.append(cube)
                                    cube_list = all_cube_list
        return cube_list
