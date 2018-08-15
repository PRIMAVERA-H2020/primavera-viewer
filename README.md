# primavera-viewer
A tool used for comparing multi-model, multi-resolution PRIMAVERA datasets. 

Variable, model and ensemble member inputs are specfied on the command line along with constraints on location and time. 

Classes and modules within the primavera-viewer package unify datasets (formatting, data types and dimension structures) allowing statistical analysis to be performed. Outputs are specified as a '.nc' file or a plot.

### Operation steps:
* STEP 1: Export a python3 conda environment
* STEP 2: Add cloned repository to `PYTHONPATH`
* STEP 3: Specify data files to read in using .json configuration files
* STEP 3: Operate tool from command line with 
```
usage: PRIMAVERA_comparison.py [-h] [-var VARIABLE [VARIABLE ...]]
                               [-mod MODELS [MODELS ...]]
                               [-ens ENSEMBLES [ENSEMBLES ...]]
                               [-stat STATISTICS] [-out OUTPUT_TYPE]
                               [-styr START_YEAR] [-enyr END_YEAR]
                               [-lat LATITUDE_POINT] [-lon LONGITUDE_POINT]
                               [-latmin LATITUDE_MIN_BOUND]
                               [-latmax LATITUDE_MAX_BOUND]
                               [-lonmin LONGITUDE_MIN_BOUND]
                               [-lonmax LONGITUDE_MAX_BOUND]

optional arguments:
  -h, --help            show this help message and exit
  -var VARIABLE [VARIABLE ...], --variable VARIABLE [VARIABLE ...]
                        input variable
  -mod MODELS [MODELS ...], --models MODELS [MODELS ...]
                        input models to compare
  -ens ENSEMBLES [ENSEMBLES ...], --ensembles ENSEMBLES [ENSEMBLES ...]
                        input ensemble members to compare
  -stat STATISTICS, --statistics STATISTICS
                        input statistics for data analysis
  -out OUTPUT_TYPE, --output_type OUTPUT_TYPE
                        type of output required from comparison tool
  -styr START_YEAR, --start_year START_YEAR
                        input start year constraint
  -enyr END_YEAR, --end_year END_YEAR
                        input end year constraint
  -lat LATITUDE_POINT, --latitude_point LATITUDE_POINT
                        input latitude point constraint
  -lon LONGITUDE_POINT, --longitude_point LONGITUDE_POINT
                        input longitude point constraint
  -latmin LATITUDE_MIN_BOUND, --latitude_min_bound LATITUDE_MIN_BOUND
                        input latitude min bound constraint
  -latmax LATITUDE_MAX_BOUND, --latitude_max_bound LATITUDE_MAX_BOUND
                        input latitude max bound constraint
  -lonmin LONGITUDE_MIN_BOUND, --longitude_min_bound LONGITUDE_MIN_BOUND
                        input longitude min bound constraint
  -lonmax LONGITUDE_MAX_BOUND, --longitude_max_bound LONGITUDE_MAX_BOUND
                        input longitude max bound constraint
```
Output is either a `.nc` file or a plot of the results

More detailed descriptions of the above arguments and operation of the primavera-viewer tool are available in the project Wiki.
