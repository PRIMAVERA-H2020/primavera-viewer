"""
Philip Rutter 03/07/18

Module for handling cube statistics, data manipulation and plotting.

Currently contains two main functions for plotting a daily and annual timeseries with ensemble means included.

Other functions below produce basic monthly and seasonal timeseries plots as well as a basic anomaly plot.

REQUIRES:
- More detailed anomaly plots with other statistical measures (stddv and max/min of yearly mean arrays)
- Method for labelling keys when comparing models as opposed to ripf scenarios.
- Check the scalings of the time axis for HadGEM3 and non-gregorian calendar models
- Storing location of nearest approximated point when comparing models

"""


import iris
import iris.coord_categorisation
import numpy as np
import iris.quickplot as qplt
import matplotlib.pyplot as plt

# plots the daily timeseries for each ensemble member and the mean ensemble
def daily_mean_timeseries(ensemble_list):
    ncubes = np.arange(0, len(ensemble_list), 1)

    # plot ensemble members mean
    for n in ncubes:
        # add new coordinate for merge and averaging process
        new_coord = iris.coords.AuxCoord(ensemble_list[n].attributes['variant_label'], long_name='ensemble_member',
                                         units='no_unit')
        ensemble_list[n].add_aux_coord(new_coord)
    # set attributes preventing merge to blank string
    attrs = ['further_info_url', 'initialization_index', 'mo_runid', 'table_info', 'variant_label']
    merge_ensemble = ensemble_list
    for cube in merge_ensemble:
        for attr in attrs:
            cube.attributes[
                attr] = ''
    merged_cube = merge_ensemble.merge_cube()
    # collapse cubes over latitude longitude and ensemble
    ensemble_mean_cube = merged_cube.collapsed(['ensemble_member','latitude','longitude'], iris.analysis.MEAN)
    qplt.plot(ensemble_mean_cube, label='ensemble mean', color='black', linestyle='dashed')

    # plot individual ensemble members
    for n in ncubes:
        single_cube = ensemble_list[n]
        # collapse cubes over latitude longitude and ensemble
        daily_mean_cube = single_cube.collapsed(['latitude','longitude'], iris.analysis.MEAN)
        # label each cube by ensemble name
        cube_label = ensemble_list[n].coord('ensemble_member').points[n]
        qplt.plot(daily_mean_cube, label=cube_label)
    plt.legend()
    plt.grid(True)

    return plt.show()




# plots the annual mean timeseries for each ensemble member and the mean ensemble
def annual_mean_timeseries(ensemble_list):
    ncubes = np.arange(0, len(ensemble_list), 1)

    # plot ensemble members mean
    for n in ncubes:
        # add new coordinate for merge and averaging process
        new_coord = iris.coords.AuxCoord(ensemble_list[n].attributes['variant_label'], long_name='ensemble_member',
                                         units='no_unit')
        ensemble_list[n].add_aux_coord(new_coord)
    # set attributes preventing merge to blank string
    attrs = ['further_info_url', 'initialization_index', 'mo_runid', 'table_info', 'variant_label']
    merge_ensemble = ensemble_list
    for cube in merge_ensemble:
        for attr in attrs:
            cube.attributes[
                attr] = ''
    merged_cube = merge_ensemble.merge_cube()
    # collapse cubes over latitude longitude and ensemble
    area_ensemble_mean = merged_cube.collapsed(['ensemble_member','latitude','longitude'], iris.analysis.MEAN)
    ensemble_mean_cube = area_ensemble_mean.aggregated_by('year', iris.analysis.MEAN)
    qplt.plot(ensemble_mean_cube, label='ensemble mean', color='black', linestyle='dashed')

    # plot individual ensemble members
    for n in ncubes:
        single_cube = ensemble_list[n]
        # collapse cubes over latitude longitude and ensemble
        cube_area_mean = single_cube.collapsed(['latitude','longitude'], iris.analysis.MEAN)
        yearly_mean_cube = cube_area_mean.aggregated_by('year', iris.analysis.MEAN)
        # label each cube by ensemble name
        cube_label = ensemble_list[n].coord('ensemble_member').points[0]
        qplt.plot(yearly_mean_cube, label=cube_label)
    plt.legend()
    plt.grid(True)

    return plt.show()










def annual_mean_anomaly_timeseries(ensemble_list):
    ncubes = np.arange(0, len(ensemble_list), 1)
    for n in ncubes:
        single_cube = ensemble_list[n]
        cube_area_mean = single_cube.collapsed(['latitude','longitude'], iris.analysis.MEAN)
        total_year_mean = cube_area_mean.collapsed('time', iris.analysis.MEAN)
        yearly_mean_cube = cube_area_mean.aggregated_by('year', iris.analysis.MEAN)
        annual_mean_anomaly = yearly_mean_cube - total_year_mean
        qplt.plot(annual_mean_anomaly, color=ncolours[n])
    return plt.show()




def monthly_mean_timeseries(ensemble_list):
    ncubes = np.arange(0, len(ensemble_list), 1)
    ncolours = ['red', 'blue', 'black', 'yellow', 'green']
    for n in ncubes:
        single_cube = ensemble_list[n]
        cube_area_mean = single_cube.collapsed(['latitude','longitude'], iris.analysis.MEAN)
        iris.coord_categorisation.add_month(cube_area_mean, 'time', 'month')
        monthly_mean_cube = cube_area_mean.aggregated_by(['month','year'], iris.analysis.MEAN)
        qplt.plot(monthly_mean_cube, color=ncolours[n])
    return plt.show()




def seasonal_mean_timeseries(ensemble_list, season=''):
    ncubes = np.arange(0, len(ensemble_list), 1)
    ncolours = ['red', 'blue', 'black', 'yellow', 'green']
    for n in ncubes:
        single_cube = ensemble_list[n]
        cube_area_mean = single_cube.collapsed(['latitude','longitude'], iris.analysis.MEAN)
        iris.coord_categorisation.add_season(cube_area_mean, 'time', 'clim_season')
        iris.coord_categorisation.add_season_year(cube_area_mean, 'time', 'season_year')
        allseason_mean_cube = cube_area_mean.aggregated_by(['clim_season','season_year'], iris.analysis.MEAN)
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
        qplt.plot(season_cube, color=ncolours[n])
    return plt.show()


