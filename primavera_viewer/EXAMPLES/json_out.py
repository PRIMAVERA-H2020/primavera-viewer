"""
Example script for producing .json configuration file relating relevant the data
directories to the CMIP6 DRS data structure.
Resulting file contained in app_config.json
"""

import json

app_config = {

    'CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LM.highresSST-present.r1i1p1f1.day'
    '.tasmax': {
        'directory': '/scratch/jseddon/primavera/stream1/CMIP6/HighResMIP/MOHC'
                     '/HadGEM3-GC31-LM/highresSST-present/r1i1p1f1/day/tasmax'
                     '/gn/v20180605/'
    },
    'CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LM.highresSST-present.r1i2p1f1.day'
    '.tasmax': {
        'directory': '/scratch/jseddon/primavera/stream1/CMIP6/HighResMIP/MOHC'
                     '/HadGEM3-GC31-LM/highresSST-present/r1i2p1f1/day/tasmax'
                     '/gn/v20180605/'
    },
    'CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LM.highresSST-present.r1i3p1f1.day'
    '.tasmax': {
        'directory': '/scratch/jseddon/primavera/stream1/CMIP6/HighResMIP/MOHC'
                     '/HadGEM3-GC31-LM/highresSST-present/r1i3p1f1/day/tasmax'
                     '/gn/v20180605/'
    },
    'CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LM.highresSST-present.r1i1p1f1.day'
    '.tasmin': {
        'directory': '/scratch/jseddon/primavera/stream1/CMIP6/HighResMIP/MOHC'
                     '/HadGEM3-GC31-LM/highresSST-present/r1i1p1f1/day/tasmin'
                     '/gn/v20180605/'
    },
    'CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LM.highresSST-present.r1i2p1f1.day'
    '.tasmin': {
        'directory': '/scratch/jseddon/primavera/stream1/CMIP6/HighResMIP/MOHC'
                     '/HadGEM3-GC31-LM/highresSST-present/r1i2p1f1/day/tasmin'
                     '/gn/v20180605/'
    },
    'CMIP6.HighResMIP.MOHC.HadGEM3-GC31-LM.highresSST-present.r1i3p1f1.day'
    '.tasmin': {
        'directory': '/scratch/jseddon/primavera/stream1/CMIP6/HighResMIP/MOHC'
                     '/HadGEM3-GC31-LM/highresSST-present/r1i3p1f1/day/tasmin'
                     '/gn/v20180605/'
    },
    'CMIP6.HighResMIP.MOHC.HadGEM3-GC31-MM.highresSST-present.r1i1p1f1.day'
    '.tasmax': {
        'directory': '/scratch/jseddon/primavera/stream1/CMIP6/HighResMIP/MOHC'
                     '/HadGEM3-GC31-MM/highresSST-present/r1i1p1f1/day/tasmax'
                     '/gn/v20170808/'
    },
    'CMIP6.HighResMIP.MOHC.HadGEM3-GC31-HM.highresSST-present.r1i1p1f1.day'
    '.tasmax': {
        'directory': '/scratch/jseddon/primavera/stream1/CMIP6/HighResMIP/MOHC'
                     '/HadGEM3-GC31-HM/highresSST-present/r1i1p1f1/day/tasmax'
                     '/gn/v20170831/'
    },
    'CMIP6.HighResMIP.CMCC.CMCC-CM2-HR4.highresSST-present.r1i1p1f1.day'
    '.tasmax': {
        'directory': '/scratch/jseddon/primavera/stream1/CMIP6/HighResMIP/CMCC'
                     '/CMCC-CM2-HR4/highresSST-present/r1i1p1f1/day/tasmax'
                     '/gn/v20170706/'
    },
    'CMIP6.HighResMIP.EC-Earth-Consortium.EC-Earth3.highresSST-present.r1i1p1f1'
    '.day.tasmax': {
        'directory': '/scratch/jseddon/primavera/stream1/CMIP6/HighResMIP'
                     '/EC-Earth-Consortium/EC-Earth3/highresSST-present/r1i1p1f1'
                     '/day/tasmax/gr/v20170911/'
    },
    'CMIP6.HighResMIP.ECMWF.ECMWF-IFS-LR.highresSST-present.r1i1p1f1.day'
    '.tasmax': {
        'directory': '/scratch/jseddon/primavera/stream1/CMIP6/HighResMIP/ECMWF'
                     '/ECMWF-IFS-LR/highresSST-present/r1i1p1f1/day/tasmax'
                     '/gr/v20170915/'
    },

}

with open('app_config.json', 'w') as fh:
    json.dump(app_config, fh, indent=2)