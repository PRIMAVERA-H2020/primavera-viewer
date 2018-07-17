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
from primavera_viewer.cube_statistics import all_experiments_mean

class TestPrimaveraViewer(unittest.TestCase):

    def setUp(self):
        self.time_constraints = [1950, 1960]  # input start/end year
        self.location_point = [20.2, 23.2, 30.5, 34.9]
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

        # Create class for experiment data at requested location
        experiments_data = ExperimentsData(experiments_list,
                                           loc=self.location_point)

        # Unify experiment spacial coordinate systems
        ed_unified_spatial_coords = experiments_data.unify_spatial_coordinates()

        # Subset experiment data at requested location
        ed_constrained_location = ed_unified_spatial_coords.constrain_location()

        # Unify format of experiment data (time dimension)
        ed_unified = ed_constrained_location.unify_cube_format()

        experiments_mean = all_experiments_mean(ed_unified
                                                .experiments_list)

        result = ExperimentsPlot(ed_unified.experiments_list, experiments_mean,
                             self.plot_type)
        result.plot_all()


if __name__ == '__main__':
    unittest.main()

