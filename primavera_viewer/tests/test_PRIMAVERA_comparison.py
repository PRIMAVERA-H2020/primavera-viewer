"""
Philip Rutter 13/07/18

Testing module for PRIMAVERA_comparison allowing python script editing rather
than command line operation

Model_input options: ['MOHC/HadGEM3-GC31-LM', 'CMCC/CMCC-CM2-HR4',
                      'EC-Earth-Consortium/EC-Earth3', 'ECMWF/ECMWF-IFS-LR']
Ensemble input options: ['r1i1p1f1', 'r1i2p1f1', 'r1i3p1f1']
Variable input options: ['tasmin', 'tasmax']
Version input options: ['gn/v20180605', 'gn/v20170808', 'gn/v20170831',
                        'gn/v20170706', 'gr/v20170911', 'gr/v20170915']

"""
import unittest
from primavera_viewer.get_PRIMAVERA_data import *
from primavera_viewer.experiments_data import *

class TestPrimaveraViewer(unittest.TestCase):

    def setUp(self):
        self.time_constraints = [1950, 1960]  # input start/end year
        self.location_point = [20.2, 30.5]
        self.choose_constraints = [self.time_constraints]
        self.experiment_inputs = Experiments(['tasmax'], 
                                             ['MOHC/HadGEM3-GC31-LM',
                                             'CMCC/CMCC-CM2-HR4',
                                             'EC-Earth-Consortium/EC-Earth3',
                                             'ECMWF/ECMWF-IFS-LR'], 
                                             ['r1i1p1f1'], 
                                             ['gn/v20180605', 'gr/v20170911',
                                               'gn/v20170706', 'gr/v20170915'])
        self.plot_type = 'annual_mean_timeseries'
        
    def test_experiment_comparison(self):
        experiments_list = self.experiment_inputs\
            .load_all_data('concatenate', self.choose_constraints)
        experiments_data = ExpStatistics(experiments_list, 
                                         loc=self.location_point) \
            .constrain_location()
        experiments_mean = ExpStatistics(experiments_data, 
                                         loc=self.location_point) \
            .all_experiments_mean()
        result = ExpPlotting(experiments_data, experiments_mean, self.plot_type)
        result.plot_all()


if __name__ == '__main__':
    unittest.main()
    
    
    
    
# time_constraints = [1950, 1960]  # input start/end year
# location_point = [30.00, 34.45, 190.78, 198.61]    # define point location
# 
# # |---- Option for constrained loading instead of post load subsetting ----|
# # lat_constraints = [60, 60]  # define latitude bounds
# # lon_constraints = [30, 30]  # define longitude bounds
# choose_constraints = [time_constraints]#, lat_constraints, lon_constraints]
# 
# # Create class containing details of all experiments
# experiment_inputs = Experiments(['tasmax'], ['MOHC/HadGEM3-GC31-LM',
#                                              'CMCC/CMCC-CM2-HR4',
#                                              'EC-Earth-Consortium/EC-Earth3',
#                                              'ECMWF/ECMWF-IFS-LR'],
#                                 ['r1i1p1f1'], ['gn/v20180605', 'gr/v20170911',
#                                                'gn/v20170706', 'gr/v20170915'])
# plot_type = 'annual_mean_timeseries'
# 
# # Load with constraints and choose to concatenate all the required files
# experiments_list = experiment_inputs.load_all_data('concatenate',
#                                                    choose_constraints)
# print('finished load')
# # Subset all cubes with requested location
# experiments_data = ExpStatistics(experiments_list, loc=location_point)\
#     .constrain_location()
# 
# # Merge multi-model/ensemble cubes and produce a mean for each time point
# experiments_mean = ExpStatistics(experiments_data, loc=location_point) \
#     .all_experiments_mean()
# 
# # Create class containing data from all experiments, the experiment mean
# # timeseries and the requested plot type
# result = ExpPlotting(experiments_data, experiments_mean, plot_type)
# 
# # Plot the data as requested
# result.plot_all()