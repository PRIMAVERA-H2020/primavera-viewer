"""
Philip Rutter 10/07/18
Module for single cube statistical methods such as annual/monthly/seasonal/zonal means
"""

import iris
import iris.coord_categorisation as icc
import numpy as np



def latitudinal_mean(cube):
    cube = cube.collapsed('latitude', iris.analysis.MEAN)
    return cube

def longitudinal_mean(cube):
    cube = cube.collapsed('longitude', iris.analysis.MEAN)
    return cube

def annual_mean(cube):
    annual_mean_cube = cube.aggregated_by('year', iris.analysis.MEAN)
    annual_mean_cube.rename(annual_mean_cube.name() + '_annual_mean')
    return annual_mean_cube

def annual_mean_max(cube):
    annual_max = cube.aggregated_by('year', iris.analysis.MAX)
    annual_max.rename(annual_max.name() + '_annual_max')
    return annual_max

def annual_mean_min(cube):
    annual_min = cube.aggregated_by('year', iris.analysis.MIN)
    annual_min.rename(annual_min.name() + '_annual_max')
    return annual_min

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