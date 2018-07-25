"""
Philip Rutter 11/07/18

PRIMAVERA data plotting operation module

Inputs:
- Start dates and end dates for the time series
- A variable to be used for plotting (only tasmax and tasmin currently
available)
- Model names and ensemble members to compare at respective resolutions
- Location. Either at a single point of reference or latitude longitude
boundaries defining an area
- Plot type

Creates an 'Experiments' class defining all of the above inputs. Uses
constrained loading to restrict timespan and loads in all required data before
concatenating. Output is a list of the cubes to be compared.

The 'ExperimentsData' class unifies the experiment's cube data (spatial
dimensions, formatting and location) in order to produce an accurate timeseries
comparison.

'ExperimentsPlotting' uses the experiments mean and plot type to visualise data.

Model_input options: ['MOHC.HadGEM3-GC31-LM', 'CMCC.CMCC-CM2-HR4',
                      'EC-Earth-Consortium.EC-Earth3', 'ECMWF.ECMWF-IFS-LR']
Ensemble input options: ['r1i1p1f1', 'r1i2p1f1', 'r1i3p1f1']
Variable input options: ['tasmin', 'tasmax']


"""
from primavera_viewer.experiments_loading import *
from primavera_viewer.experiments_data import *
from primavera_viewer.experiments_plotting import *
import argparse


def parse_args():
    """
    Parse command-line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-var', '--variables', nargs='+',
                        help='input variables to compare')
    parser.add_argument('-mod', '--models', nargs='+',
                        help='input models to compare')
    parser.add_argument('-ens', '--ensembles', nargs='+',
                        help='input ensemble members to compare')
    parser.add_argument('-plt', '--plot_type',
                        help='input plot type for data analysis')
    parser.add_argument('-syr', '--start_year',
                        help='input start year for comparison', type=int)
    parser.add_argument('-eyr', '--end_year',
                        help='input end year for comparison', type=int)
    parser.add_argument('-lat', '--latitude_point',
                        help='input latitude point for comparison', type=int)
    parser.add_argument('-lon', '--longitude_point',
                        help='input longuitude point for comparison', type=int)

    args = parser.parse_args()
    return args


def main(args):
    """
    Run comparison of models/ensembles and plot data
    """
    time_constraints = [args.start_year, args.end_year]  # input start/end year
    location_point = [args.latitude_point, args.longitude_point]    # define point location

    choose_constraints = [time_constraints]

    # Create class containing details of all experiments
    experiment_inputs = ExperimentsLoading(args.variables, args.models,
                                           args.ensembles, choose_constraints)
    experiments_list = experiment_inputs.load_all_data()

    # Create class for experiment data at requested location
    experiments_data = ExperimentsData(experiments_list, loc=location_point)

    # Unify experiment spacial coordinate systems
    experiments_data_unified = experiments_data.experiments_operations()

    experiments_mean = experiments_data_unified.all_experiments_mean()

    # Create class containing data from all experiments, the experiment mean
    # timeseries and the requested plot type
    result = ExperimentsPlotting(experiments_data_unified.experiments_list,
                                 experiments_mean, args.plot_type)

    # Plot the data as requested
    result.experiments_plot()

if __name__ == '__main__':

    args = parse_args()

    # Run the code
    main(args)