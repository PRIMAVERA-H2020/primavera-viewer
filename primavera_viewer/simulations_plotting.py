from multiprocessing import Process, Manager
import itertools
import iris
from primavera_viewer import exp_statistics as stats
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from primavera_viewer import exp_format as format
import numpy as np
from datetime import datetime
from primavera_viewer.timeseries_filter import *

class ExperimentsPlotting:
    """
    Class that containes the daily data for each experiment in a cube in
    experiments list. The mean of these experiments is also included. A
    plot_type variable is also included to described the required plot for the
    final analysis.
    """

    def __init__(self, exp_list=iris.cube.CubeList([]), loc=np.array([]),
                 exp_mean=iris.cube.Cube([]), plot='', fil=''):
        self.experiments_list = exp_list
        self.location = loc
        self.experiments_mean = exp_mean
        self.plot_type = plot
        self.filter = fil

    def annual_mean_timeseries(self, params, output):
        """
        Experiments data are aggregated by year and plotted as a timeseries for
        the requested period. Includes the experiments mean timeseries.
        """
        cube = params.get()
        annual_mean = stats.annual_mean(cube)
        output.append(annual_mean)

    def monthly_mean_timeseries(self, params, output):
        """
        Experiments data are aggregated by month and plotted as a timeseries for
        the requested period. Includes the experiments mean timeseries.
        """
        cube = params.get()
        monthly_analysis_cubes = stats.monthly_analysis(cube)
        output.append(monthly_analysis_cubes[0])

    def daily_anomaly_timeseries(self, params, output):
        """
        Calculates the anomaly timeseries for each experiment based on daily
        data. The anomaly is taken with respect to the mean from each month over
        all years for the constrained time period.
        """
        cube = params.get()
        month_anomaly = stats.daily_anomaly(cube)
        output.append(month_anomaly)

    def monthly_mean_anomaly_timeseries(self, params, output):
        """
        Calculates the anomaly timeseries for each experiment aggregated by
        month. The anomaly is taken with respect to the mean from each month
        over all years for the constrained time period.
        """
        cube = params.get()
        month_anomaly = stats.monthly_mean_anomaly(cube)
        output.append(month_anomaly)

    def monthly_maximum_anomaly_timeseries(self, params, output):
        """
        Calculates the anomaly timeseries for each experiment aggregated by
        month. The anomaly is taken with respect to the mean from each month
        over all years for the constrained time period.
        """
        cube = params.get()
        month_anomaly = stats.monthly_maximum_anomaly(cube)
        output.append(month_anomaly)

    def lighten_color(self, color, amount=0.5):
        """
        Lightens the given color by multiplying (1-luminosity) by the given amount.
        Input can be matplotlib color string, hex string, or RGB tuple.

        Examples:
        >> lighten_color('g', 0.3)
        >> lighten_color('#F034A3', 0.6)
        >> lighten_color((.3,.55,.1), 0.5)
        """
        import matplotlib.colors as mc
        import colorsys
        try:
            c = mc.cnames[color]
        except:
            c = color
        c = colorsys.rgb_to_hls(*mc.to_rgb(c))
        return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])


    def experiments_plot(self):
        """
        Performs the plotting for all experiments cubes in parallel.
        Currently has to merge cubes for anomaly plot outside of the
        parallelisation due to errors.
        """

        # Perform statistical analysis of cubes in parallel
        if self.experiments_list[0].has_lazy_data():
            print('Before plotting: cubes have lazy data')
        else:
            print('Before plotting: no lazy data')
        print('Starting plotting at time: '+str(datetime.now()))
        sttime1 = datetime.now()
        jobs = []
        manager = Manager()
        params = manager.Queue()
        result_list = manager.list()
        if self.plot_type == 'annual_mean_timeseries':
            plot_func = self.annual_mean_timeseries
            arguments = (params, result_list)
            self.experiments_list.append(self.experiments_mean)
        if self.plot_type == 'monthly_mean_timeseries':
            plot_func = self.monthly_mean_timeseries
            arguments = (params, result_list)
            self.experiments_list.append(self.experiments_mean)
        if self.plot_type == 'daily_anomaly_timeseries':
            plot_func = self.daily_anomaly_timeseries
            arguments = (params, result_list)
        if self.plot_type == 'monthly_mean_anomaly_timeseries':
            plot_func = self.monthly_mean_anomaly_timeseries
            arguments = (params, result_list)
        if self.plot_type == 'monthly_maximum_anomaly_timeseries':
            plot_func = self.monthly_maximum_anomaly_timeseries
            arguments = (params, result_list)
        max_simul_jobs = len(self.experiments_list)
        for i in range(max_simul_jobs):
            p = Process(target=plot_func, args=arguments)
            jobs.append(p)
            p.start()
        iters = itertools.chain(
            self.experiments_list, (None,) * max_simul_jobs)
        for iter in iters:
            params.put(iter)
        for j in jobs:
            j.join()
        entime1 = datetime.now()
        print('Time ellapsed when performing cube statistics: '
              + str(entime1 - sttime1))

        # Problem with merging monthly anomaly cubes inside parallel branches
        # must complete merge outside of the loop
        sttime2 = datetime.now()
        cube_list = iris.cube.CubeList([])
        if self.plot_type == 'monthly_mean_anomaly_timeseries':
            for i in np.arange(0,len(result_list),1):
                cubes = result_list[i]
                cube = cubes.merge_cube()
                cube = format.change_time_points(cube, dy=1, hr=00)
                cube_list.append(cube)
            new_cube_list = cube_list
        if self.plot_type == 'monthly_maximum_anomaly_timeseries':
            for i in np.arange(0,len(result_list),1):
                cubes = result_list[i]
                cube = cubes.merge_cube()
                cube = format.change_time_points(cube, dy=1, hr=00)
                cube_list.append(cube)
            new_cube_list = cube_list
        if self.plot_type == 'daily_anomaly_timeseries':
            for i in np.arange(0,len(result_list),1):
                cubes = result_list[i]
                cube = cubes.merge_cube()
                cube = format.change_time_points(cube, hr=00)
                cube_list.append(cube)
            new_cube_list = cube_list
        else:
            cube_list = result_list
        entime2 = datetime.now()
        print('Time ellapsed when merging cubes: '
              + str(entime2 - sttime2))

        # Plot the results of the above with the option of plotting filtered
        # results
        iris.save(new_cube_list,
                  "../primavera_data/saved_files/experiments_daily_anomaly_timeseries.nc")
        # iris.save(experiments_mean,
        #           "../saved_files/experiments_mean.nc")
        sttime3 = datetime.now()
        colours = ['r','b','#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 'c', 'm']
        for i, cube in enumerate(new_cube_list):
            if i == 0:
                col = 'r'
            if i == 1:
                col = 'b'
            cube_label = cube.coord('experiment_label').points[0]
            cube_name = cube.long_name
            if cube_label == 'Experiments Mean':
                qplt.plot(cube, color=self.lighten_color('k', 1.0),
                          linewidth=0.1)
            else:
                qplt.plot(cube, color=self.lighten_color(col, 1.0),
                          linewidth=0.1)
        entime3 = datetime.now()
        print('Time ellapsed when plotting results: '
              + str(entime3 - sttime3))
        # TAKE OUT FILTERING FOR TESTING
        # for i, cube in enumerate(new_cube_list):
        #     if i == 0:
        #         col = 'b'
        #     if i == 1:
        #         col = 'r'
        #     filtered_cube = daily_timeseries_filter(cube)
        #     cube_label = cube.coord('experiment_label').points[0]
        #     cube_name = cube.long_name
        #     if cube_label == 'Experiments Mean':
        #         qplt.plot(filtered_cube, label=cube_label, color=self.lighten_color('k', 1),
        #                   linewidth=0.3)
        #     else:
        #         qplt.plot(filtered_cube, label=cube_label, color=self.lighten_color(col, 1),
        #                   linewidth=0.3)
        # if self.filter == 'month':
        #     for i, cube in enumerate(new_cube_list):
        #         filtered_cube = monthly_timeseries_filter(cube)
        #         cube_label = cube.coord('experiment_label').points[0]
        #         if cube_label == 'Experiments Mean':
        #             qplt.plot(filtered_cube, label=cube_label, color='k',
        #                       linewidth=2.0)
        #         else:
        #             qplt.plot(filtered_cube, label=cube_label, color=colours[i],
        #                       linewidth=2.0)

        # Change final plot details
        plt.legend()
        if len(self.location) == 2:
            plt.title(cube_name+'\n'
                      'at Lat: '+str(self.location[0])+'N '
                      'Lon: '+str(self.location[1])+'E')
        if len(self.location) == 4:
            plt.title(cube_name+'\n'
                      'over Lat range: '+str(self.location[0])+'N '
                      'to '+str(self.location[1])+'N '
                      'Longitude range: '+str(self.location[2])+'E '
                      'to '+str(self.location[3])+'E')

        print('Finished plotting at time: ' + str(datetime.now()))
        if self.experiments_list[0].has_lazy_data():
            print('After plotting: cubes have lazy data\n')
        else:
            print('After plotting: no lazy data\n')
        return plt.grid(True)
