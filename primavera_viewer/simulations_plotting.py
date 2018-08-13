"""
Philip Rutter 13/08/18

Module defines a class 'SimulationsPlotting' used to perform simulation
statistics based on the require plotting function. Results are then displayed
in a plot.
"""

from multiprocessing import Process, Manager
import itertools
from primavera_viewer import sim_statistics as stats
import iris.quickplot as qplt
from primavera_viewer import sim_format as format
from datetime import datetime
from primavera_viewer.timeseries_filter import *
import sys

class SimulationsPlotting:
    """
    Class that contains the data for each simulation in a cube
    simulations list. The mean of these simulations is also included. A
    plot_type variable is included to described the required plot for the final
    analysis.
    """

    def __init__(self, sim_list=iris.cube.CubeList([]), loc=np.array([]),
                 sim_mean=iris.cube.Cube([]), stats='', out=''):
        self.simulations_list = sim_list
        self.location = loc
        self.simulations_mean = sim_mean
        self.statistics = stats
        self.output = out

    def annual_mean_timeseries(self, params, output):
        """
        Simulations data are aggregated by year and plotted as a timeseries for
        the requested period. Includes the simulations mean timeseries.
        """
        cube = params.get()
        annual_mean = stats.annual_mean(cube)
        output.append(annual_mean)

    def monthly_mean_timeseries(self, params, output):
        """
        Simulations data are aggregated by month and plotted as a timeseries for
        the requested period. Includes the simulations mean timeseries.
        """
        cube = params.get()
        monthly_analysis_cubes = stats.monthly_analysis(cube)
        output.append(monthly_analysis_cubes[0])

    def daily_anomaly_timeseries(self, params, output):
        """
        Calculates the anomaly timeseries for each simulation based on daily
        data. The anomaly is taken with respect to the mean from each month over
        all years for the constrained time period.
        """
        cube = params.get()
        month_anomaly = stats.daily_anomaly(cube)
        output.append(month_anomaly)

    def monthly_mean_anomaly_timeseries(self, params, output):
        """
        Calculates the anomaly timeseries for each simulation aggregated by
        month. The anomaly is taken with respect to the mean from each month
        over all years for the constrained time period.
        """
        cube = params.get()
        month_anomaly = stats.monthly_mean_anomaly(cube)
        output.append(month_anomaly)

    def monthly_maximum_anomaly_timeseries(self, params, output):
        """
        Calculates the anomaly timeseries for each simulation aggregated by
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


    def simulations_statistics(self):
        """
        Performs the statistics for all simulations cubes in parallel.
        Currently has to merge cubes for anomaly plot outside of the
        parallelisation due to errors.
        """

        # Perform statistical analysis of cubes in parallel
        jobs = []
        manager = Manager()
        params = manager.Queue()
        result_list = manager.list()
        if self.statistics == 'annual_mean_timeseries':
            plot_func = self.annual_mean_timeseries
            arguments = (params, result_list)
            self.simulations_list.append(self.simulations_mean)
        elif self.statistics == 'monthly_mean_timeseries':
            plot_func = self.monthly_mean_timeseries
            arguments = (params, result_list)
            self.simulations_list.append(self.simulations_mean)
        elif self.statistics == 'daily_anomaly_timeseries':
            plot_func = self.daily_anomaly_timeseries
            arguments = (params, result_list)
        elif self.statistics == 'monthly_mean_anomaly_timeseries':
            plot_func = self.monthly_mean_anomaly_timeseries
            arguments = (params, result_list)
        elif self.statistics == 'monthly_maximum_anomaly_timeseries':
            plot_func = self.monthly_maximum_anomaly_timeseries
            arguments = (params, result_list)
        else:
            print('ERROR: Specified plotting is not permitted')
            sys.exit()
        max_simul_jobs = len(self.simulations_list)
        for i in range(max_simul_jobs):
            p = Process(target=plot_func, args=arguments)
            jobs.append(p)
            p.start()
        iters = itertools.chain(
            self.simulations_list, (None,) * max_simul_jobs)
        for iter in iters:
            params.put(iter)
        for j in jobs:
            j.join()

        # Problem with merging monthly anomaly cubes inside parallel branches
        # must complete merge outside of the loop
        if self.statistics == 'monthly_mean_anomaly_timeseries':
            cube_list = iris.cube.CubeList([])
            for i in np.arange(0, len(result_list), 1):
                cubes = result_list[i]
                cube = cubes.merge_cube()
                cube = format.change_time_points(cube, dy=1, hr=00)
                cube_list.append(cube)
        elif self.statistics == 'monthly_maximum_anomaly_timeseries':
            cube_list = iris.cube.CubeList([])
            for i in np.arange(0, len(result_list), 1):
                cubes = result_list[i]
                cube = cubes.merge_cube()
                cube = format.change_time_points(cube, dy=1, hr=00)
                cube_list.append(cube)
        elif self.statistics == 'daily_anomaly_timeseries':
            cube_list = iris.cube.CubeList([])
            for i in np.arange(0, len(result_list), 1):
                cubes = result_list[i]
                cube = cubes.merge_cube()
                cube = format.change_time_points(cube, hr=00)
                cube_list.append(cube)
        else:
            cube_list = result_list
        return cube_list

    def simulations_output(self):

        result_cubes = self.simulations_statistics()
        # Optional .nc file output
        if self.output == 'net_cdf':
            # output save file to directory
            iris.save(result_cubes, 'primavera_comparison.nc',
                      netcdf_format="NETCDF3_CLASSIC")
            return result_cubes
        # Optional plot output
        if self.output == 'plot':
            # Plot the primavera comparison results
            colours = ['r','b','#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 'c', 'm']
            for i, cube in enumerate(result_cubes):
                cube_label = cube.coord('simulation_label').points[0]
                cube_name = cube.long_name
                if cube_label == 'Simulations Mean':
                    qplt.plot(cube, color=self.lighten_color('k', 1.0),
                              linewidth=1.0)
                else:
                    qplt.plot(cube, color=self.lighten_color(colours[i], 1.0),
                              linewidth=1.0)
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
            plt.grid(True)
            return plt.show()

