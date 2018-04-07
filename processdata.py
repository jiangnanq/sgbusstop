import json, re, sys, os, csv
from urllib.parse import urlparse
import httplib2 as http
from geopy.distance import vincenty
import xlrd
from natsort import natsorted
import codecs
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import requests 

__author__ = 'Nanqing'
# Class to process busstop/mall/mrt station information
# All information should been extract
# from LTA and saved to file in the data directory

class Lta:
    path = ''
    headers = {}
    uri = 'http://datamall2.mytransport.sg/ltaodataservice/'
    ltatype = {'busstop':'BusStops?$skip=',
               'busRoute':'BusRoutes?$skip=',
               'taxi':'Taxi-Availability?$skip='}

    def __init__(self):
        # init class base on the appoint class type
        with open('apikey.json')  as fp:
            keys = json.load(fp)
        self.AccountKey = keys['lta_accountkey']
        self.UniqueUserID = keys['lta_userid']
        self.headers = {
            'AccountKey': self.AccountKey,
            'UniqueUserID': self.UniqueUserID,
            'accept': 'application/json'}

    def GetDataFromLta(self, i, path):
        # send request to LTA and return reply json data
        target = urlparse(self.uri + path + i)
        print (target.geturl())
        method = 'GET'
        body = ''
        h = http.Http()
        response, content = h.request(
            target.geturl(),
            method,
            body,
            self.headers)
        jsonObj = json.loads(content)
        return jsonObj

    def readDataFromLTA(self, path):
        # Read LTA data base on the class type
        ltadata = []
        i = 0
        while True:
            step = str(i * 500)
            jsonData = self.GetDataFromLta(step, path)
            i = i+1
            a = len(jsonData['value'])
            print(i, a)
            for item in jsonData['value']:
                ltadata.append(item)
            if a < 500:
                return ltadata
    
    def readTaxiFromlta(self):
        taxi = self.readDataFromLTA('taxi')
        with open('data/ltataxi.json', 'w') as fp:
            json.dump(taxi, fp)

    def readBusRouteFromlta(self):
        busroutedata = self.readDataFromLTA('BusRoutes?$skip=')
        with open('data/ltabusroute.json', 'w') as fp:
            json.dump(busroutedata, fp)

    def readBusStopFromlta(self):
        busstopdata = self.readDataFromLTA('BusStops?$skip=')
        with open('data/ltabusstop.json', 'w') as fp:
            json.dump(busstopdata, fp)

    def checkbusarrival(self):
        with open('apikey.json')  as fp:
            keys = json.load(fp)
        key = keys['lta_accountkey']
        h = {'AccountKey': 'QbJYYDbzk2V605i6JBXPHA==', 'accept': 'application/json'}
        url = 'http://datamall2.mytransport.sg/ltaodataservice/BusArrivalv2?BusStopCode=22249'
        s = requests.Session()
        r = s.get(url, headers = h)
        print(r.text)


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

    def readareainfo(self):
        # read plan area poly shape data
        with open('inputdata/planarea.json') as fp:
            area = json.load(fp)
        allarea = {}
        for oneAread in area:
            areaname = oneAread['pln_area_n']
            areapoly = Polygon(json.loads(oneAread['geojson'])['coordinates'][0][0])
            allarea[areaname] = areapoly
        return allarea

    def readbuschn(self):
        b = {}
        with codecs.open('data/bchn.csv', 'r', 'utf-8') as fp:
            for line in fp:
                a = line.split(',')
                if len(a) == 3:
                    b[a[0].zfill(5)] = a[2].strip('\n')
        return b

    def checkArea(self, latitude, longitude, planarea):
        areaname = ''
        point = Point(longitude, latitude)
        for aname, apoly in planarea.items():
            if apoly.contains(point):
                areaname = aname
                break
        return areaname

    def processBusStops(self):
        busStops = self.readbusstops()
        busRoutes = self.readbusroute()
        Mrt = self.readmrt()
        bchn = self.readbuschn()
        planarea = self.readareainfo()
        bstop = {}
        i =0 
        for abusstop in busStops:
            i = i+1
            if i>100 and i%100==0:
                print(i)
            code = abusstop['BusStopCode']
            busstoplat = abusstop['Latitude']
            busstoplong = abusstop['Longitude']
            description = abusstop['Description']
            roadname = abusstop['RoadName']
            areaname = self.checkArea(busstoplat, busstoplong, planarea)
            chn = ''
            if code in [*bchn]:
                chn = bchn[code]
            mrts = []
            for amrtno, amrt in Mrt.items():
                mrtlat = amrt[1]
                mrtlong = amrt[2]
                if self.checkdistance(busstoplat, busstoplong, mrtlat, mrtlong, \
                    self.DistanceMrtBusstation):
                    mrts.append(amrtno)
            buses = []
            for abusroute in busRoutes:
                busstopcode = abusroute['BusStopCode']
                if code == busstopcode:
                    buses.append(abusroute['ServiceNo'])
            bs = list(set(buses) - set(['225', '243', '410']))
            bs.sort(key=self.natural_keys)
            bstop[code] = [description, chn, \
            busstoplat, busstoplong, roadname, areaname, \
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
        with open('busservice/busline.json', 'w') as fp:
            json.dump(serviceNo, fp)
        route = {}
        i = 0
        for aline in serviceNo:
            if i > 100 and i % 50 == 0: print(i)
            busstops = []
            for aBusRoute in busRoutes:
                sn = aBusRoute['ServiceNo']
                if sn == aline:
                    info = aBusRoute['BusStopCode'] + ',' + \
                    str(aBusRoute['Direction']) + ',' + \
                    str(aBusRoute['Distance']) + ',' + \
                    str(aBusRoute['StopSequence'])
                    busstops.append(info)
            route[aline] = busstops
            i = i + 1
            # fname = 'busservice/' + aline + '.json'
            # print(fname)
            # with open(fname, 'w') as fp:
            #     json.dump(route[aline], fp)
        with open('data/busroute.json', 'w')  as fp:
            json.dump(route, fp)
        return route
    
    def checkdistance(self, lat1, long1, lat2, long2, condition):
        p1 = (lat1,long1)
        p2 = (lat2,long2)
        return  vincenty(p1,p2).m < condition

    def atoi(self, text):
        try:
            return int(text)
        except:
            return text

    def natural_keys(self, text):
        return [ self.atoi(c) for c in re.split('([0-9]+)', text)]

    def busstopTranslate(self):
        busstopchn = {}
        with codecs.open('inputdata/buschn.csv', 'r', 'utf-8') as fp:
            for line in fp:
                a = line.split(',')
                busstopchn[a[0].zfill(5)] = a[3]
        return busstopchn

    def readMrtStations(self):
        # read MRT station information from excel file
        fname = dataFile.mrtStationFile
        xl_workbook = xlrd.open_workbook(os.path.expanduser(fname))
        xl_sheet = xl_workbook.sheet_by_index(0)
        num_cols = xl_sheet.ncols
        mrt = []
        for row_idx in range(0, xl_sheet.nrows):
            amrt = []
            for col_idx in range(0, num_cols):
                amrt.append(xl_sheet.cell(row_idx, col_idx).value)
            mrt.append(amrt)
        mrt.pop(0)
        mrtdict = {}
        for amrt in mrt:
            mrtnumber = str(amrt[0])
            mrtname = amrt[1]
            mrtname_chn = amrt[2]
            mrtlatitude = float(amrt[3])
            mrtlongitude = float(amrt[4])
            mrtdict[mrtnumber] = [mrtname, mrtlatitude, mrtlongitude, mrtname_chn]
        return mrtdict

print("start processing...")

# with open('data/busstop.json') as fp:
#     busstop = json.load(fp)
# with open('data/busroute.json') as fp:
#     busroute = json.load(fp)
# bus2 = []
# bus1 = []
# for abus, line in busroute.items():
#     b = list(filter(lambda x: x.split(',')[1] == '2', line))
#     if len(b) > 0:
#         bus2.append(abus)
#     else:
#         bus1.append(abus)
# allbus = {}
# for abus in bus1:
#     allbus[abus] = busroute[abus]
# for abus in bus2:
#     line = busroute[abus]
#     line1 = list(filter(lambda x: x.split(',')[1] == '1', line))
#     line2 = list(filter(lambda x: x.split(',')[1] == '2', line))
#     allbus[abus + '_1'] = line1
#     allbus[abus + '_2'] = line2
# with open('busline.json', 'w') as fp:
#     json.dump(allbus, fp)
print('process completed.')