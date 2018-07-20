"""
Philip Rutter 10/07/18
Module for single cube statistical methods such as annual/monthly/seasonal/area
means
"""

import iris
import iris.coord_categorisation as icc
import numpy as np
from primavera_viewer import cube_format as format

# def change_cube_format(cube):
#     cube = format.remove_extra_coords(cube)
#     cube = format.change_calendar(cube,
#                                   new_units='days since 1950-01-01 00:00:00')
#     cube = format.add_extra_coords(cube)
#     cube = format.unify_data_type(cube)
#     cube = format.set_blank_attributes(cube)
#     cube = format.change_time_points(cube, hr=12)
#     cube = format.change_time_bounds(cube)
#     cube.remove_coord('day_of_month')
#     cube.remove_coord('hour')
#     return cube

def all_experiments_mean(cubes):
    """
    Purpose: Calculates the multi-model/multi-ensemble mean for each time
    point for a given variable.
    :return: single cube containing multi-model/ensemble mean
    Note: All calendars are converted to a 360 day calendar by this script.
    Gregorian and 365 day calendars keep 31/01 and 31/03 to balance 28/02.
    All other 31st days and leap days are removed.
    """
    all_cubes_list = iris.cube.CubeList([])
    for cube in cubes:
        try:
            cube.remove_coord('latitude')
        except:
            pass
        try:
            cube.remove_coord('longitude')
        except:
            pass
        all_cubes_list.append(cube)
    cubes = all_cubes_list
    merged_cube = cubes.merge_cube()
    experiments_mean = merged_cube.collapsed('experiment_label',
                                             iris.analysis.MEAN)
    return experiments_mean


def latitudinal_mean(cube):
    cube = cube.collapsed('latitude', iris.analysis.MEAN)
    return cube


def longitudinal_mean(cube):
    cube = cube.collapsed('longitude', iris.analysis.MEAN)
    return cube


def annual_mean(cube):
    annual_mean_cube_list = iris.cube.CubeList([])
    annual_mean_cube = cube.aggregated_by('year', iris.analysis.MEAN)
    annual_mean_cube.rename(annual_mean_cube.name() + '_annual_mean')
    annual_mean_cube_list.append(annual_mean_cube)
    annual_max = cube.aggregated_by('year', iris.analysis.MAX)
    annual_max.rename(annual_max.name() + '_annual_max')
    annual_mean_cube_list.append(annual_max)
    annual_min = cube.aggregated_by('year', iris.analysis.MIN)
    annual_min.rename(annual_min.name() + '_annual_min')
    annual_mean_cube_list.append(annual_min)
    return annual_mean_cube_list


def monthly_mean(cube):
    monthly_mean_cube = cube.aggregated_by(['month','year'], iris.analysis.MEAN)
    monthly_max_cube = cube.aggregated_by(['month','year'], iris.analysis.MAX)
    monthly_min_cube = cube.aggregated_by(['month','year'], iris.analysis.MIN)
    return [monthly_mean_cube, monthly_max_cube, monthly_min_cube]


def monthly_anomaly(cube):
    cube = format.add_extra_time_coords(cube)
    monthly_mean_anomaly_list = iris.cube.CubeList([])
    monthly_max_anomaly_list = iris.cube.CubeList([])
    monthly_min_anomaly_list = iris.cube.CubeList([])
    all_months_mean = cube.aggregated_by(['month'], iris.analysis.MEAN)
    monthly_cubes = monthly_mean(cube)
    monthly_mean_cube = monthly_cubes[0]
    monthly_max_cube = monthly_cubes[1]
    monthly_min_cube = monthly_cubes[2]
    for mon in np.arange(1,13,1):
        cube_mean = monthly_mean_cube.extract(
            iris.Constraint(month_number=mon))
        cube_max = monthly_max_cube.extract(
            iris.Constraint(month_number=mon))
        cube_min = monthly_min_cube.extract(
            iris.Constraint(month_number=mon))
        all_month_mean = all_months_mean.extract(
            iris.Constraint(month_number=mon))
        cube_mean_anomaly = cube_mean - all_month_mean
        cube_max_anomaly = cube_max - all_month_mean
        cube_min_anomaly = cube_min - all_month_mean
        cube_mean_anomaly.rename(cube_mean.name() + '_monthly_mean_anomaly')
        cube_max_anomaly.rename(cube_max.name() + '_monthly_mean_anomaly')
        cube_min_anomaly.rename(cube_min.name() + '_monthly_mean_anomaly')
        for i, point in enumerate(cube_mean_anomaly.coord('time')):
            cube = cube_mean_anomaly[i]
            cube = format.remove_extra_time_coords(cube)
            monthly_mean_anomaly_list.append(cube)
        for i, point in enumerate(cube_max_anomaly.coord('time')):
            cube = cube_max_anomaly[i]
            cube = format.remove_extra_time_coords(cube)
            monthly_max_anomaly_list.append(cube)
        for i, point in enumerate(cube_min_anomaly.coord('time')):
            cube = cube_min_anomaly[i]
            cube = format.remove_extra_time_coords(cube)
            monthly_min_anomaly_list.append(cube)

    anomaly_mean = monthly_mean_anomaly_list.merge_cube()
    anomaly_mean = format.change_time_points(anomaly_mean, dy=1, hr = 00)
    anomaly_max = monthly_max_anomaly_list.merge_cube()
    anomaly_max = format.change_time_points(anomaly_max, dy=1, hr = 00)
    anomaly_min = monthly_min_anomaly_list.merge_cube()
    anomaly_min = format.change_time_points(anomaly_min, dy=1, hr = 00)
    return [anomaly_mean, anomaly_max, anomaly_min]


def seasonal_mean(cube):
    seasons = ['winter','summer']
    icc.add_season(cube, 'time', 'clim_season')
    icc.add_season_year(cube, 'time', 'season_year')
    season_mean_cube_list = iris.cube.CubeList([])
    season_max_cube_list = iris.cube.CubeList([])
    season_min_cube_list = iris.cube.CubeList([])
    for season in seasons:
        if season == 'winter':
            months = 'djf'
        if season == 'spring':
            months = 'mam'
        if season == 'summer':
            months = 'jja'
        if season == 'autumn':
            months = 'son'
        single_season_cube = cube.extract(iris.Constraint(clim_season=months))
        season_mean_cube = single_season_cube.aggregated_by(
            ['clim_season', 'season_year'], iris.analysis.MEAN)
        season_mean_cube.rename(season_mean_cube.name() + '_'+season+'_mean')
        season_mean_cube_list.append(season_mean_cube)
        season_max = single_season_cube.aggregated_by(
            ['clim_season', 'season_year'], iris.analysis.MAX)
        season_max.rename(season_max.name() + '_'+season+'_max')
        season_max_cube_list.append(season_max)
        season_min = single_season_cube.aggregated_by(
            ['clim_season', 'season_year'], iris.analysis.MIN)
        season_min.rename(season_min.name() + '_'+season+'_min')
        season_min_cube_list.append(season_min)
    return [season_mean_cube_list,season_max_cube_list,season_min_cube_list]
