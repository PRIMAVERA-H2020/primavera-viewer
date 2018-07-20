from primavera_viewer import cube_statistics as stats
import iris.quickplot as qplt
import matplotlib.pyplot as plt


def annual_mean_timeseries(cubes, experiments_mean):
    colours = ['r', 'b', 'g', 'c', 'm', 'y']
    for i, cube in enumerate(cubes):
        cubes = stats.annual_mean(cube)
        annual_mean = cubes[0]
        annual_mean_max = cubes[1]
        annual_mean_min = cubes[2]
        cube_label = cubes[0].coord('experiment_label').points[0]
        qplt.plot(annual_mean, label=cube_label, color=colours[i])
        qplt.plot(annual_mean_max, linestyle='dashed', color=colours[i])
        qplt.plot(annual_mean_min, linestyle='dashed', color=colours[i])
    mean_cube = stats.annual_mean(experiments_mean)
    qplt.plot(mean_cube[0], label='experiment_mean', color='black')
    plt.legend()
    plt.grid(True)
    return plt.show()


def seasonal_mean_timeseries(cubes, experiments_mean):
    colours = ['r', 'b', 'g', 'c', 'm', 'y']
    for i, cube in enumerate(cubes):
        list_season_cubes = stats.seasonal_mean(cube)
        for season_cubes in list_season_cubes:
            for season_cube in season_cubes:
                season_mean = season_cube[0]
                seasonal_mean_max = cubes[1]
                seasonal_mean_min = cubes[2]
                #cube_label = season_mean.coord('experiment_label').points[0]
                qplt.plot(season_mean, color=colours[i])#, label=cube_label)
                qplt.plot(seasonal_mean_max, color=colours[i], linestyle='dashed')
                qplt.plot(seasonal_mean_min, color=colours[i], linestyle='dashed')
    mean_cubes = stats.seasonal_mean(experiments_mean)
    for mean_cube in mean_cubes:
        qplt.plot(mean_cube, label='experiment_mean', color='black')
    plt.legend()
    plt.grid(True)
    return plt.show()


def experiments_mean_anomaly(cubes, experiments_mean):
    colours = ['r', 'b', 'g', 'c', 'm', 'y']
    for i, cube in enumerate(cubes):
        experiment_anomaly = cube - experiments_mean
        cube_label = cube.coord('experiment_label').points[0]
        qplt.plot(experiment_anomaly, label=cube_label, color=colours[i])
    plt.legend()
    plt.grid(True)
    return plt.show()


def monthly_anomaly_timeseries(cubes): #, experiments_mean):
    colours = ['r', 'b', 'g', 'c', 'm', 'y']
    for i, cube in enumerate(cubes):
        month_anomaly = stats.monthly_anomaly(cube)
        cube_label = cube.coord('experiment_label').points[0]
        qplt.plot(month_anomaly[0], label=cube_label, color=colours[i])
        # qplt.plot(month_anomaly[1], linestyle='dashed', color=colours[i])
        # qplt.plot(month_anomaly[2], linestyle='dashed', color=colours[i])
    plt.legend()
    plt.grid(True)
    return plt.show()