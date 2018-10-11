"""
PRIMAVERA_comparison.py
=======================

Philip Rutter 14/08/18

PRIMAVERA data comparison operation module

Inputs:
- Start dates and end dates for the time series
- A variable to be used for plotting (only tasmax and tasmin currently
available)
- Model names and ensemble members to compare at respective resolutions
- Location. Either at a single point of reference or latitude longitude
boundaries defining an area
- Statistical analysis type
- Output type

Create a 'SimulationsLoading' class defining all of the above inputs. Use
constrained loading to restrict time span and loads in all required data before
concatenating. Output is a list of the cubes to be compared.

The 'SimulationsData' class unifies the simulation's cube data (spatial
dimensions, formatting and location) in order to produce a time series
comparison.

'SimulationsOutput' uses the simulations mean, requested statistics and output
type to visualise finalised data for comparison.

"""
import argparse
import logging.config
import sys

import matplotlib
matplotlib.use('Agg')
from primavera_viewer.simulations_loading import *
from primavera_viewer.simulations_data import *
from primavera_viewer.simulations_output import *

DEFAULT_LOG_LEVEL = logging.WARNING
DEFAULT_LOG_FORMAT = '%(levelname)s: %(message)s'

logger = logging.getLogger(__name__)


def parse_args():
    """
    Parse command-line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-var', '--variable', nargs='+',
                        help='input variable')
    parser.add_argument('-mod', '--models', nargs='+',
                        help='input models to compare')
    parser.add_argument('-ens', '--ensembles', nargs='+',
                        help='input ensemble members to compare')
    parser.add_argument('-stat', '--statistics',
                        help='input statistics for data analysis')
    parser.add_argument('-out', '--output_type',
                        help='type of output required from comparison tool')
    parser.add_argument('--filename', help='optional prefix for the output '
                                           'filename')
    parser.add_argument('-styr', '--start_year',
                        help='input start year constraint', type=int)
    parser.add_argument('-enyr', '--end_year',
                        help='input end year constraint', type=int)
    parser.add_argument('-lat', '--latitude_point',
                        help='input latitude point constraint',
                        type=float)
    parser.add_argument('-lon', '--longitude_point',
                        help='input longitude point constraint',
                        type=float)
    parser.add_argument('-latmin', '--latitude_min_bound',
                        help='input latitude min bound constraint',
                        type=float)
    parser.add_argument('-latmax', '--latitude_max_bound',
                        help='input latitude max bound constraint',
                        type=float)
    parser.add_argument('-lonmin', '--longitude_min_bound',
                        help='input longitude min bound constraint',
                        type=float)
    parser.add_argument('-lonmax', '--longitude_max_bound',
                        help='input longitude max bound constraint',
                        type=float)
    parser.add_argument('-l', '--log-level', help='set logging level to one of '
        'debug, info, warn (the default), or error')
    args = parser.parse_args()
    return args


def main(args):
    """
    Assign command line arguments to associated exceptions.
    Run comparison of models/ensembles and plot data.
    """

    if args.variable:
        variable = args.variable
    else:
        logger.error('Must specify variable input')
        sys.exit()

    if args.models:
        models = args.models
    else:
        logger.error('Must specify models')
        sys.exit()

    if args.ensembles:
        ensembles = args.ensembles
    else:
        logger.error('Must specify ensemble members')
        sys.exit()

    if args.statistics:
        statistics = args.statistics
    else:
        logger.error('Must specify statistics')
        sys.exit()

    if args.output_type:
        output_type = args.output_type
    else:
        logger.error('Must specify output_type')
        sys.exit()

    if args.start_year and args.end_year:
        time_constraints = [args.start_year, args.end_year]
    else:
        logger.error('No time period specified')
        sys.exit()

    if args.latitude_point and args.latitude_point:
        location_constraints = [args.latitude_point,
                                args.longitude_point]
    elif args.latitude_min_bound and args.latitude_max_bound and \
            args.longitude_min_bound and args.longitude_max_bound:
        location_constraints = [args.latitude_min_bound,
                                args.latitude_max_bound,
                                args.longitude_min_bound,
                                args.longitude_max_bound]
    else:
        logger.warning('No location specified. Return global average.')
        location_constraints = [-90.0, 90.0, 0.0, 360.0]

    # Create class containing details of all simulations
    simulations_inputs = SimulationsLoading(variable, models,
                                            ensembles, time_constraints)
    simulations_list = simulations_inputs.load_all_data()

    # Create class for simulation data at requested location
    simulations_data = SimulationsData(simulations_list,
                                       loc=location_constraints,
                                       t_constr=time_constraints)

    # Unify simulation spacial coordinate systems and constrain at location
    simulations_data_unified = simulations_data.simulations_operations()

    simulations_mean = simulations_data_unified.all_simulations_mean()

    # Create class containing data from all simulations, the simulation mean,
    # the statical analysis requested and output type
    output = SimulationsOutput(simulations_data_unified.simulations_list,
                               simulations_data_unified.location,
                               simulations_mean, statistics, output_type,
                               args.filename)

    # Data output as requested
    output.simulations_result()

if __name__ == '__main__':

    cmd_args = parse_args()

    # determine the log level
    if cmd_args.log_level:
        try:
            log_level = getattr(logging, cmd_args.log_level.upper())
        except AttributeError:
            logger.setLevel(logging.WARNING)
            logger.error('log-level must be one of: debug, info, warn or error')
            sys.exit(1)
    else:
        log_level = DEFAULT_LOG_LEVEL

    # configure the logger
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': DEFAULT_LOG_FORMAT,
            },
        },
        'handlers': {
            'default': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'standard'
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': log_level,
                'propagate': True
            }
        }
    })

    # Run the code
    main(cmd_args)