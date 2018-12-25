import json
import csv
import datetime
import operator
from functools import reduce
from ltataxi import Lta_Taxi


class BusstopVolume:
    busstopvolumes = []
    mrtstopvolumes = []

    def __init__(self):
        self.busstopvolumes = self.filterData(self.readVolume('bus09.csv'))
        self.mrtstopvolumes = self.filterData(self.readVolume('train09.csv'))

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
        return volume

    def compare(self, passenger, taxi):
        c = {}
        for onearea in passenger:
            areaname = onearea[0]
            if areaname in list(map(lambda x: x[0], taxi)):
                p = onearea[1]
                t = list(filter(lambda x: x[0] == areaname, taxi))[0][1]
                c[areaname] = p-t
        return sorted(c.items(), key=operator.itemgetter(1))

__author__ = 'Nanqing'
if __name__ == '__main__':
    print('Start processing...')
    b = BusstopVolume()
    t = Lta_Taxi().checkAreaTaxi()
    v = b.countVolume()
    c = b.compare(v, t)
    with open('data/taxivolume.json', 'w') as fp:
        json.dump(c, fp)
    print('Completed.')
