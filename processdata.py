import json
import re
import sys
import os
from urlparse import urlparse
import httplib2 as http
from geopy.distance import vincenty
import xlrd
from natsort import natsorted
__author__ = 'Nanqing'
# Class to process busstop/mall/mrt station information
# All information should been extract
# from LTA and saved to file in the data directory

class ltatype:
    busstop = 'busstop'
    busroute = 'busRoute'

class lta:
    path = ''
    headers = {}
    uri = 'http://datamall2.mytransport.sg/ltaodataservice/'
    AccountKey = 'QbJYYDbzk2V605i6JBXPHA=='
    UniqueUserID = '5aa27f9b-74fd-4bb6-8f4e-3a9aa47613bb'
    ltatype = {'busstop':'BusStops?$skip=',
               'busRoute':'BusRoutes?$skip='}

    def __init__(self):
        # init class base on the appoint class type
        self.headers = {
            'AccountKey': self.AccountKey,
            'UniqueUserID': self.UniqueUserID,
            'accept': 'application/json'}
        self.loadLocalLTAdata()

    def GetDataFromLta(self, i):
        # send request to LTA and return reply json data
        target = urlparse(self.uri + self.path+i)
        print target.geturl()
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

    def readDataFromLTA(self):
        # Read LTA data base on the class type
        ltadata = []
        i = 0
        while True:
            step = str(i*50)
            jsonData = self.GetDataFromLta(step)
            i = i+1
            a = len(jsonData['value'])
            print i, a
            for item in jsonData['value']:
                ltadata.append(item)
            if a < 50:
                return ltadata
    def readBusRouteFromlta(self):
        self.path = self.ltatype['busRoute']
        busroutedata = self.readDataFromLTA()
        readWriteFile().saveF(dataFile().ltabusRouteFile, busroutedata)
        with open(os.path.expanduser(dataFile().ltabusRouteCSV), 'w') as fp:
            for abusstop in busroutedata:
                line = self.readRoute(abusstop)
                fp.write(line)
        fp.close()
    def readRoute(self, abusstop):
        code = str(abusstop['BusStopCode'])
        direction = str(abusstop['Direction'])
        Distance = str(abusstop['Distance'])
        Operator = str(abusstop['Operator'])
        satFirst = str(abusstop['SAT_FirstBus'])
        satLast = str(abusstop['SAT_LastBus'])
        sunFirst = str(abusstop['SUN_FirstBus'])
        sunLast = str(abusstop['SUN_LastBus'])
        serviceno = str(abusstop['ServiceNo'])
        stopsequence = str(abusstop['StopSequence'])
        wdFirst = str(abusstop['WD_FirstBus'])
        wdLast = str(abusstop['WD_LastBus'])
        line = code + ',' + direction + ',' + Distance + ',' + Operator + ','
        line = line + satFirst + ',' + satLast + ',' + sunFirst + ',' + sunLast + ','
        line = line + wdFirst + ',' + wdLast + ',' + serviceno + ',' + stopsequence + '\n' 
        return line
    def readstop(self, abusstop):
        code = str(abusstop['BusStopCode']).zfill(5)
        description = str(abusstop['Description'])
        latitude = str(abusstop['Latitude'])
        longitude = str(abusstop['Longitude'])
        roadname = str(abusstop['RoadName'])
        line = code + ',' + description + ',' + roadname + ',' + latitude + ',' + longitude + '\n'
        return line

    def readBusStopFromlta(self):
        self.path = self.ltatype['busstop']
        busstopdata = self.readDataFromLTA()
        readWriteFile().saveF(dataFile().ltabusStopFile, busstopdata)
        with open(os.path.expanduser(dataFile().ltabusStopCSV), 'w') as fp:
            for abusstop in busstopdata:
                line = self.readstop(abusstop)
                fp.write(line)
        fp.close()
    def loadLocalLTAdata(self):
        self.busRoutes = readWriteFile().readF(dataFile().ltabusRouteFile)
        self.busStops = readWriteFile().readF(dataFile().ltabusStopFile)
        # self.busstopTranslate()
        self.Mrt = self.readMrtStations()
        # self.bstops={}
        # for abusstop in self.busStops:
        #     code = abusstop['BusStopCode']
        #     self.bstops[code] = [abusstop['Description'], abusstop['RoadName'], abusstop['Latitude'], abusstop['Longitude']]
        #     if code in self.bstopsChn.keys():
        #         self.bstops[code].append(self.bstopsChn[code][0])
        #         self.bstops[code].append(self.bstopsChn[code][1])
        #     else:
        #         self.bstops[code].append('')
        #         self.bstops[code].append('')

    def processBusStops(self):
        bstop = {}
        i =0 
        for abusstop in self.busStops:
            i = i+1
            if i>1000 and i%1000==0:
                print i
            code = abusstop['BusStopCode']
            busstoplat = abusstop['Latitude']
            busstoplong = abusstop['Longitude']
            description = abusstop['Description']
            roadname = abusstop['RoadName']
            mrts = []
            for amrtno, amrt in self.Mrt.iteritems():
                mrtlat = amrt[1]
                mrtlong = amrt[2]
                if self.checkdistance(busstoplat, busstoplong, mrtlat, mrtlong, distance.DistanceMrtBusstation):
                    mrts.append(amrtno)
            buses = []
            for abusroute in self.busRoutes:
                busstopcode = abusroute['BusStopCode']
                if code == busstopcode:
                    buses.append(abusroute['ServiceNo'])
            bs = list(set(buses))
            bs.sort(key=self.natural_keys)
            bstop[code] = [description, busstoplat, busstoplong, roadname, len(bs), mrts, bs]
        with open('test.json', 'w') as fp:
            json.dump(b, fp)
        fp.close()
        return bstop

    def saveBusstopTofile(self):
        print ('Saving to file...')
        allbusstops = []
        with open('test.json') as fp:
            bstop = json.load(fp)
        for code,abs in bstop.iteritems():
            m = ''
            if len(abs[5])>0:
                for amrt in abs[5]:
                    m = m + amrt+':'
                m.rstrip(':')
            bs = ''
            if abs[4]>0:
                for abus in abs[6]:
                    bs = bs + abus + ':'
                bs.rstrip(':')
            abusstop = code + ',' + abs[0] + ',' + str(abs[1]) + ',' + str(abs[2]) + ',' + abs[3] \
            + ',' + str(abs[4]) + ',' + m + ',' + bs + '\n'
            allbusstops.append(abusstop)
        with open(os.path.expanduser(dataFile().localbusstop), 'w') as fp:
            for abusstop in allbusstops:
                fp.write(abusstop)
        fp.close()

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

    def combine(self):
        c = []
        for abusroute in self.busRoutes:
            code = str(abusroute['BusStopCode'])    
            if code in self.bstops.keys():
                line = self.readRoute(abusroute)
                line = line.rstrip('\n') 
                line = line + ',' + self.bstops[code][0] + ','+ self.bstops[code][1] + ','+ str(self.bstops[code][2]) + ',' \
                + str(self.bstops[code][3]) + ',' 
                line = line + self.bstops[code][4] + ',' + self.bstops[code][5] + '\n'
                c.append(line)
        with open(os.path.expanduser(dataFile().ltadataCSV), 'w') as fp:
            for item in c:
                fp.write(item.encode('gb2312'))
        fp.close()
        return
    def busstopTranslate(self):
        self.bstopsChn = {}
        xl_workbook = xlrd.open_workbook(os.path.expanduser(dataFile().busstopCHNxls))
        xl_sheet =xl_workbook.sheet_by_index(0)
        for row_index in range(1, xl_sheet.nrows):
            busstopno = str(xl_sheet.cell(row_index, 0).value).rstrip('.0')
            busstopname = xl_sheet.cell(row_index, 3).value.encode('gb2312')
            streetname = xl_sheet.cell(row_index, 4).value.encode('gb2312')
            self.bstopsChn[busstopno] = [busstopname, streetname]
        return
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

class dataFolder:
    data = '~/Dropbox/project/busstoppy/data/'
    inputData = '~/Dropbox/project/busstoppy/inputdata/'

class dataFile:
    ltabusRouteFile = dataFolder.data + 'ltabusRoutes.json'
    ltabusStopFile = dataFolder.data + 'ltabusstop.json'
    ltabusRouteCSV = dataFolder.data + 'ltabusRoutes.csv'
    ltabusStopCSV = dataFolder.data + 'ltabusStop.csv'
    ltadataCSV = dataFolder.data + 'ltadata.csv'
    busstopCHNxls = dataFolder.inputData + 'busstop_chinese.xlsx'
    mrtStationFile = dataFolder.inputData + 'MRT.xlsx'
    localbusstop = dataFolder.data + 'busstop.csv'

class distance:
    DistanceMrtBusstation = 150
    DistanceMrtMall = 300
    DistanceMallBusstation = 15

class readWriteFile:
    def readF(self, filename):
        # read json file
        with open(os.path.expanduser(filename)) as datafile:
            data = json.load(datafile)
        datafile.close()
        return data
    def saveF(self, filename, dataToSave):
        with open(os.path.expanduser(filename), 'w') as fp:
            json.dump(dataToSave, fp)
        fp.close()

a = lta()