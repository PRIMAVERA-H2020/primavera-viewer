"""
Philip Rutter 10/07/18

PRIMAVERA data plotting operation module

Inputs:
- Start dates and end dates for the time series
- A variable to be used for plotting (only tasmax and tasmin currently available)
- Model names and ensemble members to compare at respective resolutions
- Location. Either at a single point of reference or latitude longitude boundaries defining an area

Creates an 'Experiment' class defining all of the above inputs. Uses constrained loading to restrict timespan and
location and loads in all required data with the option to concatenate. Output is a list of the cubes to be compared.
The input for constrained time loading is not yet implemented.

The plot stats module holds the functions required for producing various timeseries plots by collapsing and
averaging data in cubes over time.

REQUIRES: adaptation to command line operation of input variables



"""
import getdatamodule as dm
import multicubestats as mcs
import numpy as np
import formatcubemodule as format
import singlecubestats as scs
import iris.quickplot as qplt
import matplotlib.pyplot as plt


# model_inputs = ['MOHC/HadGEM3-GC31-LM', 'CMCC/CMCC-CM2-HR4', 'EC-Earth-Consortium/EC-Earth3', 'ECMWF/ECMWF-IFS-LR']
# ensemble_inputs = ['r1i1p1f1', 'r1i2p1f1', 'r1i3p1f1']
# variable_inputs = ['tasmin', 'tasmax']
# resolution_inputs = ['gn/v20180605', 'gn/v20170808', 'gn/v20170831', 'gn/v20170706', 'gr/v20170911', 'gr/v20170915']

time_constraints = [1950,1980]  # input start/end year
location_point = [60,30]    # define point location

# |----- Option for constrained loading instead of post load subsetting -----|
# lat_constraints = [60, 60]  # define latitude bounds
# lon_constraints = [30, 30]  # define longitude bounds
choose_constraints = [time_constraints]     #, lat_constraints, lon_constraints]

choose_variables = ['tasmax']      # variable input
compare_models = ['MOHC/HadGEM3-GC31-LM', 'CMCC/CMCC-CM2-HR4']       # models input
compare_ensembles = ['r1i1p1f1','r1i2p1f1']    # ensembles input
compare_resolutions = ['gn/v20180605', 'gn/v20170706']     # version input

# create class containing all the variables to be compared
experiment_inputs = dm.Experiments(choose_variables, compare_models, compare_ensembles,  compare_resolutions)

# load with constraints and choose to concatenate all the required files
experiment_list = experiment_inputs.load_all_data('concatenate', choose_constraints)

# subset all cubes with requested location
experiment_list = mcs.locate_point_cubes(location_point, experiment_list)

# merge multi-model/ensemble cubes and produce a mean for each time point
experiment_mean = mcs.multi_experiment_mean(experiment_list)

# EXAMPLE PLOT FUNCTION FOR ANNUAL MEAN AND MAX/MIN for each year
ncubes = np.arange(0, len(experiment_list), 1)
colours = ['r', 'b', 'g']
for n in ncubes:
    # collapse cubes over latitude longitude and ensemble
    cube = experiment_list[n]
    cube = format.add_extra_coords(cube)
    annual_mean_cube = scs.annual_mean(cube)
    annual_max = scs.annual_mean_max(cube)
    annual_min = scs.annual_mean_min(cube)
    # label each cube by ensemble name
    cube_label = cube.coord('experiment_label').points[0]
    qplt.plot(annual_mean_cube, label=cube_label, color=colours[n])
    qplt.plot(annual_max, linestyle='dashed', color=colours[n])
    qplt.plot(annual_min, linestyle='dashed', color=colours[n])

annual_mean_cube = scs.annual_mean(experiment_mean)
annual_max = scs.annual_mean_max(experiment_mean)
annual_min = scs.annual_mean_min(experiment_mean)
qplt.plot(annual_mean_cube, label='experiment_mean', color='black')
qplt.plot(annual_max, linestyle='dashed', color='black')
qplt.plot(annual_min, linestyle='dashed', color='black')

plt.legend()
plt.grid(True)
plt.show()
