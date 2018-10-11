"""
sim_statistics.py
=================

Philip Rutter 13/08/18
Module for single cube statistical methods such as annual/monthly means and
anomalies.
"""
import logging
import iris
import numpy as np
from primavera_viewer import sim_format as format

logger = logging.getLogger(__name__)


def annual_mean(cube):
    """
    Creates year-by-year annual mean time series

    :param cube: iris.cube.Cube
    :return: annual mean iris.cube.Cube time series
    """
    logger.debug('getting annual mean '+
                 cube.coord('simulation_label').points[0])
    cube = format.add_extra_time_coords(cube)
    annual_mean_cube = cube.aggregated_by('year', iris.analysis.MEAN)
    annual_mean_cube.rename(annual_mean_cube.name() + '_annual_mean')
    return annual_mean_cube


def monthly_analysis(cube):
    """
    Creates month-by-month annual mean/max/min time series

    :param cube: iris.cube.Cube
    :return: monthly analysis iris.cube.Cube time series
    """
    logger.debug('getting monthly mean '+
                 cube.coord('simulation_label').points[0])
    cube = format.add_extra_time_coords(cube)
    monthly_mean_cube = cube.aggregated_by(['month','year'], iris.analysis.MEAN)
    monthly_mean_cube.rename(monthly_mean_cube.name() + '_mean')
    monthly_max_cube = cube.aggregated_by(['month','year'], iris.analysis.MAX)
    monthly_max_cube.rename(monthly_max_cube.name() + '_max')
    monthly_min_cube = cube.aggregated_by(['month','year'], iris.analysis.MIN)
    monthly_min_cube.rename(monthly_min_cube.name() + '_min')
    cube_list= iris.cube.CubeList([monthly_mean_cube, monthly_max_cube,
                                   monthly_min_cube])
    return cube_list


def daily_anomaly(cube):
    """
    Creates daily anomaly time series from all months mean over time period

    :param cube: iris.cube.Cube
    :return: daily anomaly iris.cube.Cube time series
    """
    logger.debug('getting daily anomaly '+
                 cube.coord('simulation_label').points[0])
    daily_mean_cube = format.add_extra_time_coords(cube)
    daily_mean_anomaly_list = iris.cube.CubeList([])
    all_months_mean = cube.aggregated_by(['month'], iris.analysis.MEAN)
    for mon in np.arange(1,13,1):
        cube_mean = daily_mean_cube.extract(
            iris.Constraint(month_number=mon))
        all_month_mean = all_months_mean.extract(
            iris.Constraint(month_number=mon))
        cube_mean_anomaly = cube_mean - all_month_mean
        cube_mean_anomaly.rename(cube_mean.long_name + ' Anomaly')
        for i in np.arange(0,len(cube_mean_anomaly.coord('time').points),1):
            cube = cube_mean_anomaly[i]
            cube = format.remove_extra_time_coords(cube)
            daily_mean_anomaly_list.append(cube)
    return daily_mean_anomaly_list


def monthly_mean_anomaly(cube):
    """
    Creates monthly mean time series from all months mean over time period

    :param cube: iris.cube.Cube
    :return: monthly mean anomaly iris.cube.Cube time series
    """
    logger.debug('getting monthly mean anomaly '
                 +cube.coord('simulation_label').points[0])
    cube = format.add_extra_time_coords(cube)
    monthly_mean_anomaly_list = iris.cube.CubeList([])
    all_months_mean = cube.aggregated_by(['month'], iris.analysis.MEAN)
    monthly_analysis_array = monthly_analysis(cube)
    monthly_mean_cube = monthly_analysis_array[0]
    for mon in np.arange(1,13,1):
        cube_mean = monthly_mean_cube.extract(
            iris.Constraint(month_number=mon))
        all_month_mean = all_months_mean.extract(
            iris.Constraint(month_number=mon))
        cube_mean_anomaly = cube_mean - all_month_mean
        cube_mean_anomaly.rename(cube_mean.name() + '_anomaly')
        for i in np.arange(0,len(cube_mean_anomaly.coord('time').points),1):
            cube = cube_mean_anomaly[i]
            cube = format.remove_extra_time_coords(cube)
            monthly_mean_anomaly_list.append(cube)
    # month_anomaly = monthly_mean_anomaly_list.merge_cube()
    # month_anomaly = format.change_time_points(month_anomaly, dy=1, hr=00)
    return monthly_mean_anomaly_list


def monthly_maximum_anomaly(cube):
    """
    Creates monthly maximum time series from all months mean over time period

    :param cube: iris.cube.Cube
    :return: monthly maximum anomaly iris.cube.Cube time series
    """
    logger.debug('getting monthly maximum anomaly '
                 +cube.coord('simulation_label').points[0])
    cube = format.add_extra_time_coords(cube)
    monthly_max_anomaly_list = iris.cube.CubeList([])
    all_months_mean = cube.aggregated_by(['month'], iris.analysis.MEAN)
    monthly_analysis_array = monthly_analysis(cube)
    monthly_max_cube = monthly_analysis_array[1]
    for mon in np.arange(1,13,1):
        cube_max = monthly_max_cube.extract(
            iris.Constraint(month_number=mon))
        all_month_mean = all_months_mean.extract(
            iris.Constraint(month_number=mon))
        cube_max_anomaly = cube_max - all_month_mean
        cube_max_anomaly.rename(cube_max.name() + '_anomaly')
        for i in np.arange(0,len(cube_max_anomaly.coord('time').points),1):
            cube = cube_max_anomaly[i]
            cube = format.remove_extra_time_coords(cube)
            monthly_max_anomaly_list.append(cube)
    # month_anomaly = monthly_mean_anomaly_list.merge_cube()
    # month_anomaly = format.change_time_points(month_anomaly, dy=1, hr=00)
    return monthly_max_anomaly_list


def monthly_minimum_anomaly(cube):
    """
     Creates monthly minimum time series from all months mean over time period

     :param cube: iris.cube.Cube
     :return: monthly minimum anomaly iris.cube.Cube time series
     """
    logger.debug('getting monthly minimum anomaly '
                 +cube.coord('simulation_label').points[0])
    cube = format.add_extra_time_coords(cube)
    monthly_min_anomaly_list = iris.cube.CubeList([])
    all_months_mean = cube.aggregated_by(['month'], iris.analysis.MEAN)
    monthly_analysis_array = monthly_analysis(cube)
    monthly_min_cube = monthly_analysis_array[2]
    for mon in np.arange(1,13,1):
        cube_min = monthly_min_cube.extract(
            iris.Constraint(month_number=mon))
        all_month_mean = all_months_mean.extract(
            iris.Constraint(month_number=mon))
        cube_min_anomaly = cube_min - all_month_mean
        cube_min_anomaly.rename(cube_min.name() + '_anomaly')
        for i in np.arange(0,len(cube_min_anomaly.coord('time').points),1):
            cube = cube_min_anomaly[i]
            cube = format.remove_extra_time_coords(cube)
            monthly_min_anomaly_list.append(cube)
    # month_anomaly = monthly_mean_anomaly_list.merge_cube()
    # month_anomaly = format.change_time_points(month_anomaly, dy=1, hr=00)
    return monthly_min_anomaly_list


# SEASONAL MEAN ANALYSIS
# def seasonal_mean(cube):
#     seasons = ['winter','summer']
#     icc.add_season(cube, 'time', 'clim_season')
#     icc.add_season_year(cube, 'time', 'season_year')
#     season_mean_cube_list = iris.cube.CubeList([])
#     season_max_cube_list = iris.cube.CubeList([])
#     season_min_cube_list = iris.cube.CubeList([])
#     for season in seasons:
#         if season == 'winter':
#             months = 'djf'
#         if season == 'spring':
#             months = 'mam'
#         if season == 'summer':
#             months = 'jja'
#         if season == 'autumn':
#             months = 'son'
#         single_season_cube = cube.extract(iris.Constraint(clim_season=months))
#         season_mean_cube = single_season_cube.aggregated_by(
#             ['clim_season', 'season_year'], iris.analysis.MEAN)
#         season_mean_cube.rename(season_mean_cube.name() + '_'+season+'_mean')
#         season_mean_cube_list.append(season_mean_cube)
#         season_max = single_season_cube.aggregated_by(
#             ['clim_season', 'season_year'], iris.analysis.MAX)
#         season_max.rename(season_max.name() + '_'+season+'_max')
#         season_max_cube_list.append(season_max)
#         season_min = single_season_cube.aggregated_by(
#             ['clim_season', 'season_year'], iris.analysis.MIN)
#         season_min.rename(season_min.name() + '_'+season+'_min')
#         season_min_cube_list.append(season_min)
#     return [season_mean_cube_list,season_max_cube_list,season_min_cube_list]
