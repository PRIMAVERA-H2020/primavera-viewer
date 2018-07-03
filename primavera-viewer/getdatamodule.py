"""
Philip Rutter 03/07/18

Module for constrained loading and concatenation of data from either a single ensemble member or multiple ensembles to
be compared.

"""

import os
import iris
import numpy as np
import iris.coord_categorisation as icc


# handle variable data from a single source
class SingleEnsemble:
    def __init__(self, var='', mod='', ens='', res=''):
        self.variable = var
        self.model = mod
        self.ensemble = ens
        self.resolution = res

    def set_variable(self, var):
        self.variable = var

    def set_model(self, mod):
        self.model = mod

    def set_ensemble(self, ens):
        self.ensemble = ens

    def set_resolution(self, res):
        self.resolution = res

    def __repr__(self):
        return "%s(var=%s, mod=%s, ens=%s, res=%s)" % \
               ("Single Simulation", self.variable, self.model, self.ensemble, self.resolution)

    def __str__(self):
        return "(%s, %s, %s, %s)" % (self.variable, self.model, self.ensemble, self.resolution)

    def load_data(self, concatenate='', input_constraints=np.array([[], [], []])):

        def my_callback(cube, field, filename):
            # add a categorical year coordinate to the cube
            icc.add_year(cube, 'time')

        year_arr = range(input_constraints[0][0], input_constraints[0][1], 1)

        constraints = iris.Constraint(year=lambda y: y in year_arr,
                                      latitude=lambda lat: input_constraints[1][0] <= lat <= input_constraints[1][1],
                                      longitude=lambda lon: input_constraints[2][0] <= lon <= input_constraints[2][1])

        # define driectory locations for ensemble members
        topdir = '/scratch/jseddon/primavera/stream1'
        datadir = '/CMIP6/HighResMIP/' + self.model + '/highresSST-present/' + self.ensemble \
                  + '/day/' + self.variable + '/gn/' + self.resolution + '/'
        dir = topdir + datadir

        # determine if the directory for the required file exists
        if os.path.isdir(dir) == True:
            cubes = iris.load(dir + '*.nc', constraints, callback=my_callback)
            print(cubes)
            if concatenate == 'yes':    # if concatenation of data is specified, remove the relevant attributes
                attrs = ['creation_date', 'history', 'tracking_id']
                for cube in cubes:
                    for attr in attrs:
                        cube.attributes[
                            attr] = ''
                conc_cubes = cubes.concatenate_cube()
                return conc_cubes
            elif concatenate == 'no':
                return cubes
        else:
            pass


# handle and compare variable data from multiple models, ensembles and resolutions
class MultiEnsemble:

    def __init__(self, var=list(), mod=list(), ens=list(), res=list()):
        self.variables = var
        self.models = mod
        self.ensembles = ens
        self.resolutions = res

    def set_variables(self, var):
        self.variables = var

    def set_models(self, mod):
        self.models = mod

    def set_ensembles(self, ens):
        self.ensembles = ens

    def set_resolutions(self, res):
        self.resolutions = res

    def __repr__(self):
        return "%s(var=%s, mod=%s, ens=%s, res=%s)" % \
               ("Multi Simulation", self.variables, self.models, self.ensembles, self.resolutions)

    def __str__(self):
        return "(%s, %s, %s, %s)" % (self.variables, self.models, self.ensembles, self.resolutions)

    def load_data(self, concatenate='', input_constraints=np.array([[], [], []])):

        def my_callback(cube, field, filename):
            # add a categorical year coordinate to the cube
            icc.add_year(cube, 'time')

        year_arr = range(input_constraints[0][0], input_constraints[0][1], 1)

        constraints = iris.Constraint(year=lambda y: y in year_arr,
                                      latitude=lambda lat: input_constraints[1][0] <= lat <= input_constraints[1][1],
                                      longitude=lambda lon: input_constraints[2][0] <= lon <= input_constraints[2][1])

        topdir = '/scratch/jseddon/primavera/stream1'   # top level data directory

        all_cube_list = iris.cube.CubeList([])
        conc_cube_list = iris.cube.CubeList([])

        for v in self.variables:
            for m in self.models:
                for e in self.ensembles:
                    for r in self.resolutions:

                        datadir = '/CMIP6/HighResMIP/' + str(m) + '/highresSST-present/' + str(e) \
                                  + '/day/' + str(v) + '/' + str(r) + '/'
                        dir = topdir + datadir

                        if os.path.isdir(dir) == True:
                            print('Loading ' + str(v) + ' data for model ensemble ' + str(m) + ' ' + str(
                                e) + ' at resolution ' + str(r))
                            cubes = iris.load(dir + '*.nc', constraints, callback=my_callback)
                            if concatenate == 'yes':
                                attrs = ['creation_date', 'history', 'tracking_id']
                                for cube in cubes:
                                    for attr in attrs:
                                        cube.attributes[
                                            attr] = ''
                                conc_cubes = cubes.concatenate_cube()
                                conc_cube_list.append(conc_cubes)
                                cube_list = conc_cube_list
                            elif concatenate == 'no':
                                for cube in cubes:
                                    all_cube_list.append(cube)
                                    cube_list = all_cube_list
                        else:
                            print('File for ' + str(v) + ' data for model ensemble ' + str(m) + ' ' + str(
                                e) + ' at resolution ' + str(r)+ ' does not exist')

        return cube_list
