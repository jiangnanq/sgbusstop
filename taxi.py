import json
import csv
import datetime
import operator
from functools import reduce
from ltataxi import Lta_Taxi


class BusstopVolume:
    busstopvolumes = []
    mrtstopvolumes = []

    def filterData(self, volumedata):
        n = str(datetime.datetime.now().hour)
        wd = ''
        f1 = list(filter(lambda x: x['TIME_PER_HOUR'] == n, volumedata))
        if datetime.datetime.now().isoweekday() < 6:
            wd = 'WEEKDAY'
        else:
            wd = 'WEEKENDS/HOLIDAY'
        f1 = list(filter(lambda x: x['DAY_TYPE'] == wd, f1))
        for arecord in f1:
            if arecord['PT_TYPE'] == 'TRAIN':
                if '-' in arecord['PT_CODE']:
                    arecord['PT_CODE'] = arecord['PT_CODE'].split('-')[0]
        return f1

    def readVolume(self, filename):
        volume = []
        with open('inputdata/'+filename) as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                volume.append(row)
        return volume

    def checkCurrentVolume(self, number, volumes):
        f1 = list(filter(lambda x: x['PT_CODE'] == number,
                         volumes))
        if len(f1) > 0:
            volume = [f1[0]['TOTAL_TAP_IN_VOLUME'],
                      f1[0]['TOTAL_TAP_OUT_VOLUME']]
        else:
            volume = [0, 0]
        return volume

    def countVolume(self):
        self.busstopvolumes = self.filterData(self.readVolume('bus09.csv'))
        self.mrtstopvolumes = self.filterData(self.readVolume('train09.csv'))
        busstops = {}
        mrts = {}
        with open('data/busstop.json') as fp:
            busstops = json.load(fp)
        with open('data/mrt.json') as fp:
            mrts = json.load(fp)
        volume = {}
        i = 0
        for abusstop, value in busstops.items():
            i = i + 1
            if i > 1000 and i % 1000 == 0:
                print(i)
            if value[5] != "":
                if value[5] in volume.keys():
                    volume[value[5]] += int(
                        self.checkCurrentVolume(
                            abusstop, self.busstopvolumes)[0])
                else:
                    volume[value[5]] = int(
                        self.checkCurrentVolume(
                            abusstop, self.busstopvolumes)[0])
        for amrt, value in mrts.items():
            volume[value[0][4]] += int(
                self.checkCurrentVolume(
                    amrt, self.mrtstopvolumes)[0])
        volume = sorted(volume.items(), key=operator.itemgetter(1))
        v1 = list(map(lambda x: x[1], volume))
        s = reduce((lambda x, y: x+y), v1)
        volume = list(map(lambda x: (x[0], x[1] / s * 100.0), volume))
        return volume, s

    def compare(self, passenger, taxi):
        c = {}
        for onearea in passenger:
            areaname = onearea[0]
            if areaname in list(map(lambda x: x[0], taxi)):
                p = onearea[1]
                t = list(filter(lambda x: x[0] == areaname, taxi))[0][1]
                c[areaname] = p-t
        return sorted(c.items(), key=operator.itemgetter(1))

    def top_area(self):
        t, s1 = Lta_Taxi().checkAreaTaxi()
        v, s2 = self.countVolume()
        c = self.compare(v, t)
        result = []
        for onearea in c:
            areaname = onearea[0]
            diff = '%.2f' % onearea[1]
            taxi = '%.2f' % list(filter(lambda x: x[0] == areaname, t))[0][1]
            passenger = '%.2f' % list(filter(
                lambda x: x[0] == areaname, v))[0][1]
            result.append((areaname, taxi, passenger, diff))
        return sorted(result, key=lambda x: float(x[3]), reverse=True)

    def check_area_volumn(self, areaname):
        busvolume = self.readVolume('bus09.csv')
        with open('data/busstop.json') as fp:
            busstops = json.load(fp)
        busstop_in_area = []
        for abusstop, value in busstops.items():
            if value[5] == areaname:
                busstop_in_area.append(abusstop)
        weekday = {}
        weekend = {}
        for i in range(0, 24):
            weekday[str(i)] = 0
            weekend[str(i)] = 0
        for onerow in list(filter(lambda x: x['PT_CODE'] in busstop_in_area,
                                  busvolume)):
            if onerow['DAY_TYPE'] == 'WEEKDAY':
                weekday[onerow['TIME_PER_HOUR']] += int(
                    onerow['TOTAL_TAP_IN_VOLUME'])
            else:
                weekend[onerow['TIME_PER_HOUR']] += int(
                    onerow['TOTAL_TAP_IN_VOLUME'])
        return list(weekday.values()), list(weekend.values())


__author__ = 'Nanqing'
if __name__ == '__main__':
    print('Start processing...')
#   weekday, weekend = BusstopVolume().check_area_volumn('JURONG WEST')
    b = BusstopVolume().top_area()
    print(b)
    print('Completed.')
