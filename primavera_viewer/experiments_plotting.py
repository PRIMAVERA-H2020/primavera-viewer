from multiprocessing import Process, Manager
import itertools
import iris
from primavera_viewer import cube_statistics as stats
import iris.quickplot as qplt
import matplotlib.pyplot as plt
from primavera_viewer import cube_format as format
import numpy as np

class ExperimentsPlotting:
    """
    Class that containes the daily data for each experiment in a cube in
    experiments list. The mean of these experiments is also included. A
    plot_type variable is also included to described the required plot for the
    final analysis.
    """

    def __init__(self, exp_list=iris.cube.CubeList([]),
                 exp_mean=iris.cube.Cube, plot=''):
        self.experiments_list = exp_list
        self.experiments_mean = exp_mean
        self.plot_type = plot


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
        monthly_mean = stats.monthly_mean(cube)
        output.append(monthly_mean)

    # # Need to adapt these functions into parallel processed format
    # def seasonal_mean_timeseries(self, cubes, experiments_mean):
    #     colours = ['r', 'b', 'g', 'c', 'm', 'y']
    #     for i, cube in enumerate(cubes):
    #         list_season_cubes = stats.seasonal_mean(cube)
    #         for season_cubes in list_season_cubes:
    #             for season_cube in season_cubes:
    #                 season_mean = season_cube[0]
    #                 seasonal_mean_max = cubes[1]
    #                 seasonal_mean_min = cubes[2]
    #                 #cube_label = season_mean.coord('experiment_label').points[0]
    #                 qplt.plot(season_mean, color=colours[i])#, label=cube_label)
    #                 qplt.plot(seasonal_mean_max, color=colours[i], linestyle='dashed')
    #                 qplt.plot(seasonal_mean_min, color=colours[i], linestyle='dashed')
    #     mean_cubes = stats.seasonal_mean(experiments_mean)
    #     for mean_cube in mean_cubes:
    #         qplt.plot(mean_cube, label='experiment_mean', color='black')
    #     plt.legend()
    #     plt.grid(True)
    #     return plt.show()
    #
    #
    # def experiments_mean_anomaly(self, params, output, experiments_mean):
    #     cube = params.get()
    #     experiment_anomaly = cube - experiments_mean
    #     print(experiment_anomaly)
    #     output.append(experiment_anomaly)


    def daily_anomaly_timeseries(self, params, output):
        """
        Calculates the anomaly timeseries for each experiment based on daily
        data. The anomaly is taken with respect to the mean from each month over
        all years for the constrained time period.
        """
        cube = params.get()
        month_anomaly = stats.daily_anomaly(cube)
        output.append(month_anomaly)


    def monthly_anomaly_timeseries(self, params, output):
        """
        Calculates the anomaly timeseries for each experiment aggregated by
        month. The anomaly is taken with respect to the mean from each month
        over all years for the constrained time period.
        """
        cube = params.get()
        month_anomaly = stats.monthly_anomaly(cube)
        output.append(month_anomaly)


    def experiments_plot(self):
        """
        Performs the plotting for all experiments cubes in parallel.
        Currently has to merge cubes for anomaly plot outside of the
        parallelisation due to errors.
        """

        print('Starting plotting')
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
        if self.plot_type == 'monthly_anomaly_timeseries':
            plot_func = self.monthly_anomaly_timeseries
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

        # Problem with merging monthly anomaly cubes inside parallel branches
        # must complete merge outside of the loop
        if self.plot_type == 'monthly_anomaly_timeseries':
            cube_list =iris.cube.CubeList([])
            for i in np.arange(0,len(result_list),1):
                cubes = result_list[i]
                cube = cubes.merge_cube()
                cube = format.change_time_points(cube, dy=1, hr=00)
                cube_list.append(cube)
            print(cube_list)
        if self.plot_type == 'daily_anomaly_timeseries':
            cube_list =iris.cube.CubeList([])
            for i in np.arange(0,len(result_list),1):
                cubes = result_list[i]
                cube = cubes.merge_cube()
                cube = format.change_time_points(cube, hr=00)
                cube_list.append(cube)
            print(cube_list)
        else:
            cube_list = result_list

        colours = ['r', 'b', 'g', 'c', 'm', 'y']
        for i, cube in enumerate(cube_list):
            cube_label = cube.coord('experiment_label').points[0]
            if cube.coord('experiment_label').points[0] == 'Experiments Mean':
                qplt.plot(cube, label=cube_label, color='k', linewidth=0.5)
            else:
                qplt.plot(cube, label=cube_label, color=colours[i],
                          linewidth=0.5)
        plt.legend()
        plt.grid(True)
        return plt.show()