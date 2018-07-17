"""
Philip Rutter 10/07/18
Main module for formatting individual cubes processing unit conversions,
additional coordinates, calendars, other time dimension issues and data types
"""

import iris
import iris.coord_categorisation as icc
import numpy as np
from cf_units import Unit


def add_experiment_label(cube):
    new_coord = iris.coords.AuxCoord(cube.attributes['source_id'] + ' ' +
                                     cube.attributes['variant_label'],
                                     long_name='experiment_label',
                                     units='no_unit')
    cube.add_aux_coord(new_coord)
    return cube


def redefine_spatial_coords(cube):
    """
    Redefines the latitude and longitude points for the EC-Earth3 model
    into single, rather than multi-dimensional, coordinates.
    """
    experiment_label = cube.coord('experiment_label').points[0]

    if experiment_label == 'EC-Earth3 r1i1p1f1':
        # procedure for handling EC-Earth latitude conversion
        cube.coord('cell index along second dimension').points = cube.coord(
            'latitude').points[:,0]
        cube.remove_coord('latitude') # remove AuxCoord 'latitude'
        cube.coord('cell index along second dimension') \
            .rename('latitude') # assign DimCoord 'latitude'
        cube.coord('latitude').units = Unit('degrees')
        cube.coord('latitude').long_name = 'latitude'
        cube.coord('latitude').var_name = 'lat'
        cube.coord('latitude').guess_bounds()
        # procedure for handling EC-earth longitude conversion
        cube.coord('cell index along first dimension').points = cube.coord(
            'longitude').points[0,:]
        cube.remove_coord('longitude') # remove AuxCoord 'longitude'
        cube.coord('cell index along first dimension') \
            .rename('longitude') # assign DimCoord 'longitude'
        cube.coord('longitude').units = Unit('degrees')
        cube.coord('longitude').long_name = 'longitude'
        cube.coord('longitude').var_name = 'lon'
        cube.coord('longitude').guess_bounds()
        return cube
    else:
        return cube






def add_extra_coords(cube):
    """
    Adds new coordinate for indexing a given experiment based on model and
    ensemble and adds additional time coordinates for unit manipulation
    """
    if not cube.coords('month_number'):
        icc.add_month_number(cube, 'time')
    if not cube.coords('day_of_month'):
        icc.add_day_of_month(cube, 'time')
    if not cube.coords('hour'):
        icc.add_hour(cube, 'time')
    return cube

def remove_extra_coords(cube):
    """
    Removes the coordinates defined above to revert cube back to its original
    coordinates
    """
    try:
        cube.remove_coord('month_number')
    except:
        pass
    try:
        cube.remove_coord('day_of_month')
    except:
        pass
    try:
        cube.remove_coord('hour')
    except:
        pass
    try:
        cube.remove_coord('height')
    except:
        pass
    return cube

def change_time_units(cube, new_units):
    """
    Purpose: Alters a cube's time units to ensure that all cubes from varying
    models and ensemble members share the same units.
    :param cube: iris.cube.Cube
    :return: cube with newly defined units
    """
    time_coord = cube.coord('time')
    new_time_unit = Unit(new_units,
                         calendar=time_coord.units.calendar)
    time_coord.convert_units(new_time_unit)
    return cube

def convert_365day_to_360day(cube):
    """
    What it does  : Convert the input calendar (assumed to be Gregorian) into a
    360day calendar for Met Office model

    How to use it : `convert_gregorian_to_360day(cube)`

    Example       : `cube = convert_gregorian_to_360day(cube)`

    Who           : Malcolm Roberts, Added by Segolene Berthou

    :param iris.cube.Cube cube: input cube of data with gregorian calendar
    :returns: 360day calendar cube
    """
    # these are tuples of (month, day) discarded by the 360 day calendar
    tunit = cube.coord('time').units
    if tunit.calendar == '365_day':
        disallowed_days = [(5, 31), (7, 31), (8, 31), (10, 31), (12, 31)]
    if tunit.calendar == 'gregorian' or 'proleptic_gregorian':
        disallowed_days = [(2, 29), (5, 31), (7, 31), (8, 31), (10, 31),
                           (12, 31)]

    def doy_365_to_360(cell):
        """
        derive all (month,day) tuples that will remain in 360 day calendar
        """

        p_dt = cell.point
        # p_dt = tunit.num2date(p)
        p_tuple = (p_dt.month, p_dt.day)
        return not p_tuple in disallowed_days

    # make constraint to exclude days and extract those days
    doy_365_to_360_con = iris.Constraint(time=doy_365_to_360)
    return cube.extract(doy_365_to_360_con)

def change_calendar(cube, new_units):
    """
    Purpose: Converts a list of cubes with varying calendars (gregorian,
    365_day, 360_day) to 360 day calendars by removing extra dates and replacing
    time axis with new points defined from the start of 1950. This allows a
    merge of a cube list containing multimodel cubes.
    :param cubes: iris.cube.CubeList
    :return: cube list with all cubes defined with the same units and a 360 day
    calendar.
    """
    if cube.coord('time').units.calendar == '360_day':
        cube = change_time_units(cube, new_units)
        return cube
    else:
        cube = convert_365day_to_360day(cube)
        # add new set of coordinates so that dates are consistent
        cube.remove_coord('time')
        npoints = len(cube.coord('year').points)
        new_points = np.arange(0, npoints, 1)
        time_coord = iris.coords.DimCoord(new_points, standard_name='time',
                                          long_name='time',
                                          var_name='time',
                                          units=Unit(new_units,
                                                     calendar='360_day'))
        cube.add_dim_coord(time_coord, 0)
        cube.coord('time').guess_bounds()
        return cube

def change_time_points(cube, yr=None, mn=None, dy=None, hr=None):
    """
    Purpose: alter's a cube's time points to ensure all cubes share the same
    date definitions

    Example: cube = change_time_points(cube, yr=None, mn=None, dy=1, hr=0) fixes
    all time points in cube to the first of each month at midnight.

    :param cube: iris.cube.Cube
    :param yr: fixes all data points at defined year
    :param mn: fixes all data points at defined month
    :param dy: fixes all data points at defined day
    :param hr: fixes all data points at defined hour
    :return: cube with time points fixed with constraints above
    """
    new_points = cube.coord('time').units.num2date(cube.coord('time').points)
    years = cube.coord('year').points
    months = cube.coord('month_number').points
    month_day = cube.coord('day_of_month').points
    hours = cube.coord('hour').points
    dates_converted = []
    for date, year, month, day, hour in zip(new_points, years, months,
                                            month_day, hours):
        if yr is not None:
            year = yr
        if mn is not None:
            month = mn
        if dy is not None:
            day= dy
        if hr is not None:
            hour = hr
        dates_converted.append(date.replace(year=year, month=month, day=day,
                                            hour=hour))
    cube.coord('time').points = cube.coord('time').units\
        .date2num(dates_converted)
    return cube

def change_time_bounds(cube):
    """
    Purpose: alter's a cube's time bounds to ensure all cubes share the same
    definitions for time bounds matching the above changes to time points.
    """
    cube.coord('time').bounds = None
    cube.coord('time').guess_bounds()
    return cube

def set_blank_attributes(cube):
    """
    removes all the cube attributes that prevent cubes merging
    """
    attributes = ['further_info_url', 'initialization_index', 'mo_runid',
                  'table_info', 'variant_label', 'CDO', 'parent_activity_id',
                  'parent_experiment_id', 'original_name', 'contact',
                  'branch_method', 'variant_info','CDI', 'references',
                  'parent_mip_era', 'data_specs_version', 'grid', 'institution',
                  'institution_id', 'nominal_resolution', 'source', 'source_id',
                  'title', 'license', 'cmor_version', 'branch_time_in_parent',
                  'branch_time_in_child', 'parent_time_units', 'member_id',
                  'parent_source_id', 'parent_variant_label','grid_label',
                  'source_type', 'run_variant', 'branch_time']
    for attr in attributes:
        cube.attributes[attr] = ''
    return cube


def unify_data_type(cube):
    """
    360 day, 365 day and gregorian calendars have different data types.
    To merge cubes, set data type to a 32bit float.
    """
    cube.data = np.float32(cube.data)
    return cube




