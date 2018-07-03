"""
Philip Rutter 03/07/18

PRIMAVERA data plotting operation module

Inputs:
- Start dates and end dates for the time series
- A variable to be used for plotting (only tasmax and tasmin currently available)
- Model names and ensemble members to compare at respective resolutions
- Location. Either at a single point of reference or latitude longitude boundaries defining an area
- Plot type (yearly mean, monthly mean, seasonal mean, anomaly plots)

Creates a 'MultiEnsemble' class defining all of the above inputs. Uses constrained loading to restrict timespan and
location and loads in all required data with the option to concatenate. Output is a list of the cubes to be compared.
The input for constrained time loading is not yet implemented.

The plot stats module holds the functions required for producing various timeseries plots by collapsing and
averaging data in cubes over time.

REQUIRES: adaptation to command line operation of input variables



"""
import getdatamodule as dm
import plotstats as pst

# model_inputs = ['MOHC/HadGEM3-GC31-LM', 'CMCC/CMCC-CM2-HR4', 'EC-Earth-Consortium/EC-Earth3', 'ECMWF/ECMWF-IFS-LR']
# ensemble_inputs = ['r1i1p1f1', 'r1i2p1f1', 'r1i3p1f1']
# variable_inputs = ['tasmin', 'tasmax']
# resolution_inputs = ['gn/v20180605', 'gn/v20170808', 'gn/v20170831', 'gn/v20170706', 'gr/v20170911', 'gr/v20170915']

# input start/end year, min/max latitude and min/max longitude
choose_constraints = [[1961, 2012], [65, 81], [306, 330]]   # roughly a region over Greenland

choose_variables = ['tasmax']      # variable input
compare_models = ['MOHC/HadGEM3-GC31-LM']       # model input
compare_ensembles = ['r1i1p1f1', 'r1i2p1f1', 'r1i3p1f1']    # ensembles input
compare_resolutions = ['gn/v20180605']     # resolution input

# create class containing all the variables to be compared
ensemble_inputs = dm.MultiEnsemble(choose_variables, compare_models, compare_ensembles,  compare_resolutions)

# load with constraints and choose to concatenate all the required files
ensemble_list = ensemble_inputs.load_data('yes', choose_constraints)

print('Starting plotting function')
# function applied to the list of cubes for required plot
pst.annual_mean_timeseries(ensemble_list)
