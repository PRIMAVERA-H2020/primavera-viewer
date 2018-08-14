"""
simulations_loading.py
======================

Philip Rutter 14/08/18

Module for loading and concatenation of data from multiple models and ensembles
for a given variable.

"""
import warnings
import json
from multiprocessing import Process, Manager
import itertools
import iris
import numpy as np
from primavera_viewer.sim_format import (add_simulation_label,
                                         change_time_units)
from datetime import datetime
import sys

# Ignore warnings displayed when loading data
warnings.filterwarnings("ignore")

# Load in json file containing data dirs
FILENAME = 'app_config.json'
# Read the config file in
with open(FILENAME) as fh:
    app_config = json.load(fh)

class SimulationsLoading:
    """
    A class of simulations for a given variable defined by a model and ensemble
    member and a time constraint. Data for each simulation can be loaded,
    constrained in time and concatenated into a single cube to be held in a
    output cube list.

    Paths to each directory containing data can be altered in the json file
    'app_config.json'. Each pathway is linked to the corresponding CMIP6 data
    reference syntax (DRS).
    """
    def __init__(self, var=list(), mod=list(), ens=list(), constr=np.array([])):
        """
        Initialise the class and create a list of the requested simulations that
        exist in the JSON configuration file.

        :param list var: Single variable (or multiple) in DRS format
        <variable_id>
        :param list mod: Models for comparison in DRS format
        <institution_id>.<source_id>
        :param list ens: Ensembles relating to above models required for comparison
        in DRS format <member_id>
        :param np.array constr: Time bounds for constraining data. A two element
        numpy array in the format ([start year, end year])
        """
        self.variable = var
        self.models = mod
        self.ensembles = ens
        self.constraints = constr
        self.simulations_list = list()
        for v in self.variable:
            for m in self.models:
                for e in self.ensembles:
                    variable = str(v)
                    model = str(m)
                    ensemble = str(e)
                    data_required = 'CMIP6.HighResMIP.'+model+\
                                    '.highresSST-present.'+ensemble+'.day.'\
                                    +variable
                    # Create list of available simulations given data exists
                    try:
                        dir = app_config[data_required]['directory']
                        simulation = [model, ensemble, variable]
                        self.simulations_list.append(simulation)
                    except:
                        print('Directory for '+model+'.'+ensemble+'.'
                              +variable+' does not exist')
                        pass
                    if not self.simulations_list:
                        print('ERROR: Specifed simulations do not exist')
                        sys.exit()

    def set_variable(self, var):
        self.variable = var

    def set_models(self, mod):
        self.models = mod

    def set_ensembles(self, ens):
        self.ensembles = ens

    def set_constraints(self, constr):
        self.constraints = constr

    def __repr__(self):
        return 'Simulations:\n{simulations}'.format(
            simulations = self.simulations_list)

    def __str__(self):
        return 'Simulations:\n{simulations}'.format(
            simulations = self.simulations_list)

    def concatenate_data(self, cubes):
        """
        Concatenates data for a single simulation.
        :param iris.cube.CubeList cubes: A cube list of single cubes from a
        single simulation forming a data set contiguous over the specified time
        constraints
        :return iris.cube.Cube: A single cube from the concatenated cube list
        """
        attributes = ['creation_date', 'history', 'tracking_id', 'realm']
        for cube in cubes:
            # set attributes likely to disrupt concatenate to a blank string
            cube = change_time_units(cube, 'days since 1950-01-01 00:00:00')
            for attr in attributes:
                cube.attributes[
                    attr] = ''
        return cubes.concatenate_cube()

    def load_data(self, params, output):
        """
        Loads data with defined constraints on time (year) for single simulation
        assuming data directory can be found in the .json file. Each load
        operation performed in parallel.

        :param list params: A list in the format ['model','ensemble','variable']
        :param iris.cube.CubeList output: CubeList to contain loaded,
        concatenated data for all simulations
        :return iris.cube.Cube: A single cube loaded and concatenated with
        simulation data
        """
        simulation = params.get()
        # constrain over the required time
        constraints = iris.Constraint(time=lambda cell: self.constraints[0]
                                                        <= cell.point.year <
                                                        self.constraints[1])
        data_required = 'CMIP6.HighResMIP.'+simulation[0]+\
                        '.highresSST-present.'+simulation[1]+'.day.'\
                        +simulation[2]
        dir = app_config[data_required]['directory']
        print('Loading '+simulation[2]+' data for model ensemble '+simulation[0]
              +' '+simulation[1])
        cubes = iris.load(dir + '/*.nc', constraints)
        cubes_diff_units = iris.cube.CubeList([])
        for cube in cubes:
            cube = change_time_units(cube, 'days since 1950-01-01 00:00:00')
            cubes_diff_units.append(cube)
        # Concatenate data if file structure requires
        if len(cubes) > 1:
            cube = self.concatenate_data(cubes_diff_units)
        else:
            cube = cubes[0]
        # Add an aux coord unique to each simulation
        cube = add_simulation_label(cube)
        output.append(cube)

    def load_all_data(self):
        """
        Loads data all simulations in self.simulations_list in parallel.

        :return iris.cube.CubeList: cube list of fully loaded and concatenated
        data from each simulation
        """
        sttime = datetime.now()
        print('Starting loading all at: '+str(sttime))
        max_simul_jobs = len(self.simulations_list)
        jobs = []
        manager = Manager()
        params = manager.Queue()
        result_list = manager.list()
        for i in range(max_simul_jobs):
            p = Process(target=self.load_data, args=(params, result_list))
            jobs.append(p)
            p.start()
        iters = itertools.chain(self.simulations_list,(None,) * max_simul_jobs)
        for iter in iters:
            params.put(iter)
        for j in jobs:
               j.join()
        cube_list = iris.cube.CubeList(list(result_list))
        entime = datetime.now()
        print('Finished loading all at: '+str(entime))
        return cube_list