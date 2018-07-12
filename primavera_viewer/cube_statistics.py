"""
Philip Rutter 10/07/18
Module for single cube statistical methods such as annual/monthly/seasonal/zonal means
"""

import iris
import iris.coord_categorisation as icc
import numpy as np
from primavera_viewer import format_cube as format

def change_cube_format(cube):
    cube = format.change_calendar(cube)
    cube = format.add_extra_coords(cube)
    cube = format.unify_data_type(cube)
    cube = format.set_blank_attributes(cube)
    cube = format.change_time_points(cube, hr=12)
    cube.remove_coord('day_of_month')
    cube.remove_coord('height')
    return cube

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
    monthly_mean_cube = cube.aggregated_by('month', iris.analysis.MEAN)
    return monthly_mean_cube

def seasonal_mean(cube, season=''):
    icc.add_season(cube, 'time', 'clim_season')
    icc.add_season_year(cube, 'time', 'season_year')
    allseason_mean_cube = cube.aggregated_by(['clim_season', 'season_year'], iris.analysis.MEAN)
    season_mean_cube = iris.cube.CubeList([])
    if season == 'winter':
        st = 0
        sep = 4
    elif season == 'spring':
        st = 1
        sep = 4
    elif season == 'summer':
        st = 2
        sep = 4
    elif season == 'autumn':
        st = 3
        sep = 4
    else:
        st = 0
        sep = 1
    season_array = np.arange(st, len(allseason_mean_cube.coord('time').points), sep)
    for s in season_array:
        season_mean_cube.append(allseason_mean_cube[s])
    season_cube = season_mean_cube.merge_cube()
    return season_cube

def experiment_mean_anomaly(cube, experiment_mean):
    anomaly = cube - experiment_mean