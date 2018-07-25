"""
Philip Rutter 25/07/18

Module for loading and concatenation of data from multiple models aand ensembles
for a given variable.

"""
from __future__ import print_function
import json
from multiprocessing import Process, Manager
import itertools
import iris
import numpy as np
from primavera_viewer.exp_format import (add_experiment_label,
                                         change_time_units)

print('get json')
FILENAME = '../app_config.json'
# Read the config file in
with open(FILENAME) as fh:
    app_config = json.load(fh)
print('got json')


class ExperimentsLoading:
    """
    A class of experiments defined by a model and an ensemble member at a given
    resolution for a single variable. Data for each experiment can be loaded,
    constrained in time and concatenated into a single cube to be held in a
    output cube list.

    Paths to each directory containing data can be altered in the json file
    'app_config.json'. Each pathway is linked to the corresponding CMIP6 data
    reference syntax.
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
                        # create a list of available experiments data
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
        Concatenates data for a single experiment.
        """
        attributes = ['creation_date', 'history', 'tracking_id', 'realm']
        for cube in cubes:
            # set attributes likely to disrupt concatenate to a blank string
            for attr in attributes:
                cube.attributes[
                    attr] = ''
        return cubes.concatenate_cube()

    def load_data(self, params, output):
        """
        Loads data with defined constraints on time (year) for single experiment
        assuming data directory can be found in the .json file.
        """
        experiment = params.get()
        # constrain over the required time
        constraints = iris.Constraint(time=lambda cell: self.constraints[0][0]
                                                        <= cell.point.year <
                                                        self.constraints[0][1])
        data_required = 'CMIP6.HighResMIP.'+experiment[0]+\
                        '.highresSST-present.'+experiment[1]+'.day.'\
                        +experiment[2]
        dir = app_config[data_required]['directory']
        print('Loading '+experiment[2]+' data for model ensemble '+experiment[0]
              +' '+experiment[1])
        cubes = iris.load(dir + '*.nc', constraints)
        cubes_diff_units = iris.cube.CubeList([])
        for cube in cubes:
            cube = change_time_units(cube, 'days since 1950-01-01 00:00:00')
            cubes_diff_units.append(cube)
        cube = self.concatenate_data(cubes_diff_units)
        # Add an aux coord unique to each experiment
        cube = add_experiment_label(cube)
        output.append(cube)

    def load_all_data(self):
        """
        Loads data all experiments in self.experiments_list in parallel.
        Returns: cube list with single cube per experiment
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