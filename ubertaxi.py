import sqlite3
from datetime import datetime
from statistics import mean
from area import Area
from functools import reduce
from taxi import BusstopVolume
import numpy


class uberdata:
    sqlite_file = 'inputdata/taxiaid.sqlite'

    def __init__(self):
        self.conn = sqlite3.connect(self.sqlite_file)
        self.c = self.conn.cursor()
        self.tn = 'uberprice'
        self.cn = 'area'

    def queryArea(self, areaname):
        self.c.execute('SELECT * FROM {tn} WHERE {cn}={an}'
                       .format(tn=self.tn, cn=self.cn, an=areaname))
        weekday = {}
        weekend = {}
        for i in range(0, 24):
            weekday[str(i)] = []
            weekend[str(i)] = []
        for onerow in self.c.fetchall():
            dt = datetime.strptime(onerow[2][0:18], '%Y-%m-%d %H:%M:%S')
            h = str(dt.hour)
            if dt.isoweekday() <= 5:
                weekday[h].append(onerow[3])
            else:
                weekend[h].append(onerow[3])
        price_weekday = {}
        price_weekend = {}
        for i in range(0, 24):
            h = str(i)
            if len(weekday[h]) == 0 or len(weekend[h]) == 0:
                price_weekday[h] = 0
                price_weekend[h] = 0
            else:
                price_weekday[h] = mean(weekday[h])
                price_weekend[h] = mean(weekend[h])
        return list(price_weekday.values()), list(price_weekend.values())


def check_area_data(areadata):
    if reduce(
        (lambda x, y: x + y), areadata[0]) == 0\
       or reduce(
            (lambda x, y: x + y), areadata[1]) == 0:
        return False
    else:
        return True

if __name__ == '__main__':
    print('start to process')
    areadata = {}
    for onearea in Area().allarea.keys():
        areadata[onearea] = uberdata().queryArea('"' + onearea + '"')
    areadata = {k: v for k, v in areadata.items() if check_area_data(v)}
    area_corr = {}
    for areaname, data in areadata.items():
        weekday, weekend = BusstopVolume().check_area_volumn(areaname)
        corr = numpy.corrcoef(data[0], weekday)[0][1]
        area_corr[areaname] = corr
        print(areaname, corr)
    print('process completed.')
