"""
Philip Rutter 02/07/18

Module for constrained loading and concatenation of data from either a single
ensemble member or multiple ensembles to be compared.

"""
from __future__ import print_function
import json
from multiprocessing import Process, Manager
import itertools
import iris
import numpy as np
import iris.coord_categorisation as icc
from primavera_viewer.cube_format import (add_experiment_label,
                                          change_time_units)


print('get json')
FILENAME = '../app_config.json'
# Read the config file in
with open(FILENAME) as fh:
    app_config = json.load(fh)
print('got json')


class Experiments:
    """
    A class of experiments with data that can be loaded individually,
    concatenated and combined into a cube list for
    multiple models, ensembles and versions at varying resolutions for a single
    variable.
    """
    def __init__(self, var=list(), mod=list(), ens=list(), constr=np.array([])):
        self.variable = var
        self.models = mod
        self.ensembles = ens
        self.constraints = constr
        self.experiments_list = list()
        for v in self.variable:
            for m in self.models:
                for e in self.ensembles:
                    model = str(m)
                    ensemble = str(e)
                    variable = str(v)
                    data_required = 'CMIP6.HighResMIP.'+model+\
                                    '.highresSST-present.'+ensemble+'.day.'\
                                    +variable
                    try:
                        dir = app_config[data_required]['directory']
                        experiment = [model, ensemble, variable]
                        self.experiments_list.append(experiment)
                    except:
                        pass

    def set_variable(self, var):
        self.variable = var

    def set_models(self, mod):
        self.models = mod

    def set_ensembles(self, ens):
        self.ensembles = ens

    def set_constraints(self, constr):
        self.constraints = constr

    def __repr__(self):
        return 'Experiments:\n{experiments}'.format(
            experiments = self.experiments_list)


    def __str__(self):
        return 'Experiments:\n{experiments}'.format(
            experiments = self.experiments_list)

    def concatenate_data(self, cubes):
        """
        Concatenates data cubes for all experiments
        """
        attributes = ['creation_date', 'history', 'tracking_id', 'realm']
        for cube in cubes:
            for attr in attributes:
                cube.attributes[
                    attr] = ''
        return cubes.concatenate_cube()

    def load_data(self, params, output):
        """
        Loads data with defined constraints on time (year), latitude and
        longitude for single experiment.
        Returns cube list
        """
        experiment = params.get()
        def my_callback(cube, field, filename):
            # add a categorical year coordinate to the cube
            icc.add_year(cube, 'time')
        year_arr = range(self.constraints[0][0], self.constraints[0][1], 1)
        constraints = iris.Constraint(year=lambda y: y in year_arr)
        data_required = 'CMIP6.HighResMIP.'+experiment[0]+\
                        '.highresSST-present.'+experiment[1]+'.day.'\
                        +experiment[2]
        dir = app_config[data_required]['directory']
        print('Loading '+experiment[2]+' data for model ensemble '+experiment[0]
              +' '+experiment[1])
        cubes = iris.load(dir + '*.nc', constraints, callback=my_callback)
        cubes_diff_units = iris.cube.CubeList([])
        for cube in cubes:
            cube = change_time_units(cube, 'days since 1950-01-01 00:00:00')
            cubes_diff_units.append(cube)
        cube = self.concatenate_data(cubes_diff_units)
        cube = add_experiment_label(cube)
        output.append(cube)

    def load_all_data(self):
        """
        Loads data for multiple experiments based on constraints for time
        (year) or latitude and longitude.
        Option to concatenate experiment cubes if required.
        Returns: A cube list
        """
        print('Starting loading all')
        max_simul_jobs = len(self.experiments_list)
        jobs = []
        manager = Manager()
        params = manager.Queue()
        result_list = manager.list()
        for i in range(max_simul_jobs):
            p = Process(target=self.load_data, args=(params, result_list))
            jobs.append(p)
            p.start()
        iters = itertools.chain(self.experiments_list,(None,) * max_simul_jobs)
        for iter in iters:
            params.put(iter)
        for j in jobs:
               j.join()
        cube_list = iris.cube.CubeList(list(result_list))
        print('Finished loading all')
        return cube_list