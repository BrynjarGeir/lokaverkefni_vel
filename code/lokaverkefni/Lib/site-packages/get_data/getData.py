import cdsapi
import subprocess

c = cdsapi.Client()

c.retrieve(
    'reanalysis-carra-height-levels',
    {
        'format' : 'grib',
        'domain' : 'west_domain',
        'variable' : [
            'pressure', 'temperature', 'wind_direction', 'wind_speed'
        ],
        'height_level' : [
            '150_m', '15_m', '250_m', '500_m'
        ],
        'product_type' : 'analysis',
        'time' : ['00:00', '12:00'],
        'year' : '2023',
        'day' : ['01', '30'],
        'month' : ['01', '06'],
    },
    'test.grib'
)

# This gets Carra height data for some period of time
# For given heights, 15m, 150m, 250m and 500m and variables pressure, tempearture, wind direction and wind speed
def getDataCarraHeight(time, date, month, year):
    format, domain, variables = 'grib', 'west_domain', ['pressure', 'temperature', 'wind_direction', 'wind_speed']
    height_level, product_type, time = ['150m', '15m', '250m', '500_m'], 'analysis'

    if type(time) is list:
        time0, time1 = time[0], time[-1]
        time_name = [time0, time1].join('-')
    else:
        time_name = time
    
    if type(date) is list:
        date0, date1 = date[0], date[-1]
        date_name = [date0, date1].join('-')
    else:
        date_name = date
    
    if type(month) is list:
        month0, month1 = month[0], month[-1]
        month_name = [month0, month1].join('-')
    else:
        month_name = month
    
    if type(year) is list:
        year0, year1 = year[0], year[-1]
        year_name = [year0, year1].join('-')
    else:
        year_name = year

    filename = time_name + '_' + date_name + '_' + month_name + '_' + year_name + '.grib'

    c = cdsapi.Client(
        'reanalysis-carra-height-levels',
        {
            'format' : format,
            'domain' : domain,
            'variable' : variables,
            'height_level' : height_level,
            'product_type' : product_type,
            'time' : time,
            'year' : year,
            'day' : date,
            'month' : month
        },
        filename
    )

    c.retrieve()    

def getDataVedur(path = 'https://brunnur.vedur.is/pub/arason/brynjar/', subset = None, tp = 'klst'):
    if subset != None:
        for station in subset:
            if tp == 'klst':
                for station in subset:
                    file = 'f_klst_' + station + '.txt'
                    result = subprocess.run(['wget', '-P', '../data', path + file])

    else:
        if tp == 'klst':
            with open('../data/stod_klst.txt') as f:
                stations = [line.strip() for line in f.readlines()]

            for station in stations:
                file = 'f_klst_' + station + '.txt'
                subprocess.run(['wget', '-P', '../data/klst', path + file])

        elif tp == '10min':
            with open('../data/stod_10min.txt') as f:
                stations = [line.rstrip() for line in f.readlines()]

            for station in stations:
                file = 'f_10min_' + station + '.txt'
                subprocess.run(['wget', '-P', '../data/min', path + file])

        elif tp == 'vg':
            with open('../data/stod_vg.txt') as f:
                stations = [line.rstrip() for line in f.readlines()]

            for station in stations:
                file = 'f_vg_' + station + '.txt'
                result = subprocess.run(['wget', '-P', '../data/vg', path + file])



