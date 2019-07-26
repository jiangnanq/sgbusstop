import json
import re
from geopy.distance import vincenty
import codecs
from area import Area

__author__ = 'Nanqing'
# Class to process busstop/mall/mrt station information
# All information should been extract
# from LTA and saved to file in the data directory


class Local:
    DistanceMrtBusstation = 150

    def readbusstops(self):
        with open('data/ltabusstop.json') as fp:
            b = json.load(fp)
        return b

    def readbusroute(self):
        with open('data/ltabusroute.json') as fp:
            b = json.load(fp)
        return b

    def readmrt(self):
        with open('data/mrt.json') as fp:
            m = json.load(fp)
        return m

    def readbuschn(self):
        b = {}
        with codecs.open('data/bchn.csv', 'r', 'utf-8') as fp:
            for line in fp:
                a = line.split(',')
                if len(a) == 3:
                    b[a[0].zfill(5)] = a[2].strip('\n')
        return b

    def processBusStops(self):
        busStops = self.readbusstops()
        busRoutes = self.readbusroute()
        Mrt = self.readmrt()
        bchn = self.readbuschn()
        areas = Area()
        bstop = {}
        i = 0
        for abusstop in busStops:
            i = i+1
            if i > 100 and i % 100 == 0:
                print(i)
            code = abusstop['BusStopCode']
            busstoplat = abusstop['Latitude']
            busstoplong = abusstop['Longitude']
            description = abusstop['Description']
            roadname = abusstop['RoadName']
            areaname = areas.checkArea(float(busstoplat), float(busstoplong))
            chn = ''
            if code in [bchn]:
                chn = bchn[code]
            mrts = []
            for amrtno, amrt in Mrt.items():
                mrtlat = amrt[0][1]
                mrtlong = amrt[0][2]
                if self.checkdistance(busstoplat, busstoplong, mrtlat, mrtlong,
                                      self.DistanceMrtBusstation):
                    mrts.append(amrtno)
            buses = []
            for abusroute in busRoutes:
                busstopcode = abusroute['BusStopCode']
                if code == busstopcode:
                    if abusroute['Direction'] == 1:
                        buses.append(abusroute['ServiceNo'])
                    else:
                        buses.append(abusroute['ServiceNo'] + '_2')
            bs = list(set(buses) - set(
                ['225', '243', '410', '225_2', '243_2', '410_2']))
            bs.sort(key=self.natural_keys)
            bstop[code] = [description, chn,
                           busstoplat, busstoplong, roadname, areaname,
                           len(bs), mrts, bs]
        with open('data/busstop.json', 'w') as fp:
            json.dump(bstop, fp)
        return bstop

    def processBusLines(self):
        busRoutes = self.readbusroute()
        serviceNo = []
        for aBusRoute in busRoutes:
            sn = aBusRoute['ServiceNo']
            if sn in serviceNo:
                continue
            else:
                serviceNo.append(sn)

        serviceNo = list(set(serviceNo) - set(['225', '243', '410']))

        with open('busservice/ltabusline.json', 'w') as fp:
            json.dump(serviceNo, fp)
        route = {}
        i = 0
        for aline in serviceNo:
            if i > 100 and i % 50 == 0:
                print(i)
            busstops = []
            busstops2 = []
            for aBusRoute in busRoutes:
                sn = aBusRoute['ServiceNo']
                if sn == aline:
                    info = [aBusRoute['BusStopCode'],
                            str(aBusRoute['Direction']),
                            str(aBusRoute['Distance']),
                            str(aBusRoute['StopSequence'])]
                    if info[2] == 'None':
                        print(info)
                        b = []
                        if info[1] == '1':
                            b = busstops
                        else:
                            b = busstops2
                        print(len(b))
                        if len(b) == 0:
                            print('replace none value')
                            info[2] = '0'
                        else:
                            info[2] = b[-1][2]
                        print(info)

                    if info[1] == '1':
                        busstops.append(info)
                    else:
                        busstops2.append(info)
            route[aline] = busstops
            if len(busstops2) > 0:
                route[aline + '_2'] = busstops2
            i = i + 1
            # fname = 'busservice/' + aline + '.json'
            # print(fname)
            # with open(fname, 'w') as fp:
            #     json.dump(route[aline], fp)
        with open('data/busroute.json', 'w') as fp:
            json.dump(route, fp)
        return route

    def checkdistance(self, lat1, long1, lat2, long2, condition):
        p1 = (float(lat1), float(long1))
        p2 = (float(lat2), float(long2))
        return vincenty(p1, p2).m < condition

    def atoi(self, text):
        try:
            return int(text)
        except ImportError:
            return 0
        return text

    def natural_keys(self, text):
        return [self.atoi(c) for c in re.split('([0-9]+)', text)]

    def busstopTranslate(self):
        busstopchn = {}
        with codecs.open('inputdata/buschn.csv', 'r', 'utf-8') as fp:
            for line in fp:
                a = line.split(',')
                busstopchn[a[0].zfill(5)] = a[3]
        return busstopchn


if __name__ == '__main__':
    print("start processing...")
    Local().processBusStops()
#    Local().processBusLines()
    print('process completed.')
