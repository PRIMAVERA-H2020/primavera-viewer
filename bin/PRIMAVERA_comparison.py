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
constrained loading to restrict timespan
and loads in all required data with the option to concatenate. Output is a list
of the cubes to be compared.

The 'ExpStatistics' class allows for constraints on location by subsetting cubes
 as well as taking multi-model/ensemble
timeseries means.

'ExpPlotting' required an input for the type of plot required and produces a
visualisation of all data as well as
max/min data for annual timeseries.

Model_input options: ['MOHC/HadGEM3-GC31-LM', 'CMCC/CMCC-CM2-HR4',
                      'EC-Earth-Consortium/EC-Earth3', 'ECMWF/ECMWF-IFS-LR']
Ensemble input options: ['r1i1p1f1', 'r1i2p1f1', 'r1i3p1f1']
Variable input options: ['tasmin', 'tasmax']
Version input options: ['gn/v20180605', 'gn/v20170808', 'gn/v20170831',
                        'gn/v20170706', 'gr/v20170911', 'gr/v20170915']


"""
from primavera_viewer.get_PRIMAVERA_data import *
from primavera_viewer.experiments_data import *
from primavera_viewer.cube_statistics import all_experiments_mean
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
    parser.add_argument('-ver', '--versions', nargs='+',
                        help='input version numbers')
    parser.add_argument('-plt', '--plot_type',
                        help='input plot type for data analysis')
    parser.add_argument('-syr', '--start_year',
                        help='input start year for comparison', type=int)
    parser.add_argument('-eyr', '--end_year',
                        help='input end year for comparison', type=int)
    parser.add_argument('-lat', '--latitude',
                        help='input latitude for comparison', type=int)
    parser.add_argument('-lon', '--longitude',
                        help='input longuitude for comparison', type=int)

    args = parser.parse_args()

    return args

def main(args):
    """
    Run comparison of models/ensembles and plot data
    """

    time_constraints = [args.start_year, args.end_year]  # input start/end year
    location_point = [args.latitude, args.longitude]    # define point location

    # |---- Option for constrained loading instead of post load subsetting ----|
    # lat_constraints = [60, 60]  # define latitude bounds
    # lon_constraints = [30, 30]  # define longitude bounds
    choose_constraints = [time_constraints]#, lat_constraints, lon_constraints]

    # Create class containing details of all experiments
    experiment_inputs = Experiments(args.variables, args.models, args.ensembles,
                                    args.versions)

    # Load with constraints and choose to concatenate all the required files
    experiments_list = experiment_inputs.load_all_data('concatenate',
                                                       choose_constraints)

    # Create class for experiment data at requested location
    experiments_data = ExperimentsData(experiments_list, loc=location_point)

    # Unify experiment spacial coordinate systems
    ed_unified_spatial_coords = experiments_data.unify_spatial_coordinates()

    # Subset experiment data at requested location
    ed_constrained_location = ed_unified_spatial_coords.constrain_location()

    # Unify format of experiment data (time dimension)
    ed_unified = ed_constrained_location.unify_cube_format()

    experiments_mean = all_experiments_mean(ed_unified)

    # Create class containing data from all experiments, the experiment mean
    # timeseries and the requested plot type
    result = ExperimentsPlot(experiments_data, experiments_mean, args.plot_type)

    # Plot the data as requested
    result.plot_all()

if __name__ == '__main__':

    args = parse_args()

    # Run the code
    main(args)