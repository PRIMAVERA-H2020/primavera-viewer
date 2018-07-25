"""
Philip Rutter 10/07/18
Module for single cube statistical methods such as annual/monthly/seasonal/area
means
"""

import iris
import iris.coord_categorisation as icc
import numpy as np
from primavera_viewer import exp_format as format


def annual_mean(cube):
    print('getting annual mean')
    cube = format.add_extra_time_coords(cube)
    annual_mean_cube = cube.aggregated_by('year', iris.analysis.MEAN)
    annual_mean_cube.rename(annual_mean_cube.name() + '_annual_mean')
    return annual_mean_cube


def monthly_mean(cube):
    print('getting monthly mean')
    cube = format.add_extra_time_coords(cube)
    monthly_mean_cube = cube.aggregated_by(['month','year'], iris.analysis.MEAN)
    monthly_mean_cube.rename(monthly_mean_cube.name() + '_monthly_mean')
    return monthly_mean_cube


def daily_anomaly(cube):
    print('getting daily anomaly')
    cube = format.add_extra_time_coords(cube)
    daily_mean_anomaly_list = iris.cube.CubeList([])
    all_months_mean = cube.aggregated_by(['month'], iris.analysis.MEAN)
    daily_mean_cube = cube
    for mon in np.arange(1,13,1):
        cube_mean = daily_mean_cube.extract(
            iris.Constraint(month_number=mon))
        all_month_mean = all_months_mean.extract(
            iris.Constraint(month_number=mon))
        cube_mean_anomaly = cube_mean - all_month_mean
        cube_mean_anomaly.rename(cube_mean.name() + '_daily_mean_anomaly')
        for i in np.arange(0,len(cube_mean_anomaly.coord('time').points),1):
            cube = cube_mean_anomaly[i]
            cube = format.remove_extra_time_coords(cube)
            daily_mean_anomaly_list.append(cube)
    return daily_mean_anomaly_list


def monthly_mean_anomaly(cube):
    print('getting monthly anomaly')
    cube = format.add_extra_time_coords(cube)
    monthly_mean_anomaly_list = iris.cube.CubeList([])
    all_months_mean = cube.aggregated_by(['month'], iris.analysis.MEAN)
    monthly_mean_cube = monthly_mean(cube)
    for mon in np.arange(1,13,1):
        cube_mean = monthly_mean_cube.extract(
            iris.Constraint(month_number=mon))
        all_month_mean = all_months_mean.extract(
            iris.Constraint(month_number=mon))
        cube_mean_anomaly = cube_mean - all_month_mean
        cube_mean_anomaly.rename(cube_mean.name() + '_monthly_mean_anomaly')
        for i in np.arange(0,len(cube_mean_anomaly.coord('time').points),1):
            cube = cube_mean_anomaly[i]
            cube = format.remove_extra_time_coords(cube)
            monthly_mean_anomaly_list.append(cube)
    # month_anomaly = monthly_mean_anomaly_list.merge_cube()
    # month_anomaly = format.change_time_points(month_anomaly, dy=1, hr=00)
    return monthly_mean_anomaly_list




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
