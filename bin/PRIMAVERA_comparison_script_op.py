"""
PRIMAVERA_comparison_script_op.py
=================================

Philip Rutter 13/07/18

Operation module for PRIMAVERA_comparison allowing python script editing rather
than command line operation
MUST CHANGE LOCATION OF JSON FILE TO: '../app_config.json'

Model_input options: ['MOHC/HadGEM3-GC31-LM', 'MOHC/HadGEM3-GC31-MM',
                      'MOHC/HadGEM3-GC31-HM', 'CMCC/CMCC-CM2-HR4',
                      'EC-Earth-Consortium/EC-Earth3', 'ECMWF/ECMWF-IFS-LR']
Ensemble input options: ['r1i1p1f1', 'r1i2p1f1', 'r1i3p1f1']
Variable input options: ['tasmin', 'tasmax']
Statistics input options: 'annual_mean_timeseries', 'monthly_mean_timeseries'
                    'daily_anomaly_timeseries',
                    'monthly_mean_anomaly_timeseries',
                    'monthly_maximum_anomaly_timeseries'
Output options: 'net_cdf', 'plot'
"""



from primavera_viewer.simulations_loading import *
from primavera_viewer.simulations_data import *
from primavera_viewer.simulations_output import *
from datetime import datetime


def main():
    startTime = datetime.now()

    time_constraints = [1950, 1960] # define time constraints in years
    location_point = [-90.0, 90.0, 0, 360.0]    # define point or area location

    # Create class containing details of all simulations
    simulation_inputs = SimulationsLoading(['tasmax'],
                                    ['MOHC.HadGEM3-GC31-LM'],
                                    ['r1i1p1f1'],
                                    time_constraints)

    # Load with constraints and concatenate all the required files
    simulations_list = simulation_inputs.load_all_data()

    # Create class for simulation data at requested location
    simulations_data = SimulationsData(simulations_list,
                                       loc = location_point,
                                       t_constr = time_constraints)

    # Unify simulation spacial coordinate systems and formatting
    simulations_data_unified = simulations_data.simulations_operations()

    # Calculate all simulations time series mean
    simulations_mean = simulations_data_unified.all_simulations_mean()

    # Create class for performing statistics and outputting result
    result = SimulationsOutput(simulations_data_unified.simulations_list,
                               simulations_data_unified.location,
                               simulations_mean,
                               stats = 'monthly_mean_anomaly_timeseries',
                               out = 'net_cdf')

    # output result
    result.simulations_result()
    time_elapsed = datetime.now() - startTime

    print('Total elapsed time: '+str(time_elapsed))

if __name__ == '__main__':
    main()
