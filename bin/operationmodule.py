"""
Philip Rutter 11/07/18

PRIMAVERA data plotting operation module

Inputs:
- Start dates and end dates for the time series
- A variable to be used for plotting (only tasmax and tasmin currently available)
- Model names and ensemble members to compare at respective resolutions
- Location. Either at a single point of reference or latitude longitude boundaries defining an area
- Plot type

Creates an 'Experiments' class defining all of the above inputs. Uses constrained loading to restrict timespan
and loads in all required data with the option to concatenate. Output is a list of the cubes to be compared.

The 'ExpStatistics' class allows for constraints on location by subsetting cubes as well as taking multi-model/ensemble
timeseries means.

'ExpPlotting' required an input for the type of plot required and produces a visualisation of all data as well as
max/min data for annual timeseries.

REQUIRES: adaptation to command line operation of input variables



"""
import getdatamodule as dm
import experimentsmodule as expm



# model_inputs = ['MOHC/HadGEM3-GC31-LM', 'CMCC/CMCC-CM2-HR4', 'EC-Earth-Consortium/EC-Earth3', 'ECMWF/ECMWF-IFS-LR']
# ensemble_inputs = ['r1i1p1f1', 'r1i2p1f1', 'r1i3p1f1']
# variable_inputs = ['tasmin', 'tasmax']
# resolution_inputs = ['gn/v20180605', 'gn/v20170808', 'gn/v20170831', 'gn/v20170706', 'gr/v20170911', 'gr/v20170915']

time_constraints = [1970,1980]  # input start/end year
location_point = [60,30]    # define point location

# |----- Option for constrained loading instead of post load subsetting -----|
# lat_constraints = [60, 60]  # define latitude bounds
# lon_constraints = [30, 30]  # define longitude bounds
choose_constraints = [time_constraints]     #, lat_constraints, lon_constraints]
choose_variables = ['tasmax']      # variable input
compare_models = ['MOHC/HadGEM3-GC31-LM', 'CMCC/CMCC-CM2-HR4']       # models input
compare_ensembles = ['r1i1p1f1','r1i2p1f1']    # ensembles input
compare_resolutions = ['gn/v20180605', 'gn/v20170706']     # version input
choose_plot_type = 'annual mean timeseries'

# Create class containing all the variables to be compared for each experiment
experiment_inputs = dm.Experiments(choose_variables, compare_models, compare_ensembles,  compare_resolutions)

# Load with constraints and choose to concatenate all the required files
experiments_list = experiment_inputs.load_all_data('concatenate', choose_constraints)

# Create class containing experiment list and required location
cubes = expm.ExpStatistics(experiments_list, loc=location_point)

# Subset all cubes with requested location
experiments_data = cubes.constrain_location()

# Merge multi-model/ensemble cubes and produce a mean for each time point
experiments_mean = expm.ExpStatistics(experiments_data, loc=location_point).all_experiments_mean()

# Create class containing data from all experiments, the experiment mean timeseries and the requested plot type
result = expm.ExpPlotting(experiments_data, experiments_mean, choose_plot_type)

# Plot the data as requested
result.plot_all()
