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

class busRoute:
    specialBus = ['243','410','225']
    ltaDataFile = dataFolder.data + 'busRoutesLta.json'
    localDataFile = dataFolder.data + 'busline.json'
    busRouteCSV = dataFolder.data + 'ltaBusRoutes.csv'
    busStopOfRoutes_lta = {}
    busRoutes = {}  #dict, busnumber:[busstopnumber, distance, direction, sequence],......
    def __init__(self, type):
        if type == 'lta':
            self.readBusRoutesFromLta()
        else:
            self.busRoutes = self.readBusRoutes()
            self.busStopOfRoutes_lta = readWriteFile().readF(self.ltaDataFile)

    def readBusRoutesFromLta(self):
        ltadata = lta(ltatype.busroute).readDataFromLTA()
        readWriteFile().saveF(self.ltaDataFile, ltadata)

    def saveBusRoutesToCSV(self):
        with open(os.path.expanduser(self.busRouteCSV), 'w') as fp:
            for abusstop in self.busStopOfRoutes_lta:
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
                fp.write(line)
        fp.close()
    def convertBusRoutes(self, buslines):   # convert dict to busline file format
        busroutes = {}
        for busnumber, busdetails in buslines.iteritems():
            busroutes[busnumber] = ''
            for abusstop in busdetails:
                details = abusstop[0]+':' +abusstop[1] + ':' +abusstop[2] + ':' +abusstop[3]
                busroutes[busnumber] = busroutes[busnumber] + details + ','
            busroutes[busnumber] = busroutes[busnumber][:-1]
        return busroutes

    def checkBuslines(self):
        t = self.busRoutes
        status = False
        for busNumber, busDetails in self.busRoutes.iteritems():
            for idx, abusstop in enumerate(busDetails):
                if idx == 0:
                    continue
                else:
                    previousStop = busDetails[idx-1]
                    if previousStop[2] == abusstop[2]:
                        if (float(previousStop[1])>float(abusstop[1]) or int(previousStop[3]) > int(abusstop[3])):
                            status = True
                            print busNumber, abusstop[0], previousStop[1],abusstop[1],previousStop[3],abusstop[3]
                            t[busNumber][idx][1]=previousStop[1]
        if status:
            readWriteFile().saveF(self.localDataFile,self.convertBusRoutes(t))

    def readBusRoutes(self):
        buslineraw = readWriteFile().readF(self.localDataFile)
        allbuslines = {}
        for key, value in buslineraw.iteritems():
            a = []
            allstops = value.split(',')
            for eachStops in allstops:
                aStop = eachStops.split(':')
                a.append(aStop)
            allbuslines[key] = a
        for aspebus in self.specialBus:
            del allbuslines[aspebus]
        return allbuslines

    def processBusRoutes(self):
        # process bus routes from LTA data
        # Generate data to busline.json
        busStopOfRoutes_lta = readWriteFile().readF(self.ltaDataFile)
        busroutes = {}
        for abusstop in busStopOfRoutes_lta:
            if abusstop['Distance'] is not None:
                busnumber = abusstop['ServiceNo']
                details = abusstop['BusStopCode'] + ':' + str(abusstop['Distance'])
                details = details + ':' + str(abusstop['Direction'])
                details = details + ':' + str(abusstop['StopSequence'])
                if busnumber in busroutes:
                    busroutes[busnumber] = busroutes[busnumber] + ',' + details
                else:
                    busroutes[busnumber] = details
        fn = dataFolder.data + 'busline.json'
        readWriteFile().saveF(fn, busroutes)

class busStop:
    localDataFileName = dataFolder.data + 'busstopforapp.json'
    ltaDataFileName = dataFolder.data + 'busstop.json'
    ltaDataFileNameCSV = dataFolder.data + 'ltabusstop.csv'
    busStops_lta = {}   #dict, busstopnumber: [description, roadname], [latitude, longitude]
    busStops = {}       #dict , filter  lta data, remove busstop without location info
    streetName = {}      #dict, streetname_eng: streetname_chn
    def __init__(self, type):
        if type == 'lta':
            self.getBusStopDataFromLta()
        else:
            self.streetName = self.readStreetName()
            self.busStops_lta = self.readBusStopFromLta()
            self.busStops = self.readBusStops()

    def getBusStopDataFromLta(self):
        busstops = lta(ltatype.busstop).readDataFromLTA()
        readWriteFile().saveF(self.ltaDataFileName,bussstops)
        busstopsraw = readWriteFile().readF(self.ltaDataFileName)
        with open(self.ltaDataFileNameCSV, 'w') as fp:
            for abusstop in busstopsraw:
                code = str(abusstop['BusStopCode']).zfill(5)
                description = str(abusstop['Description'])
                latitude = str(abusstop['Latitude'])
                longitude = str(abusstop['Longitude'])
                roadname = str(abusstop['RoadName'])
                line = code + ',' + description + ',' + roadname + ',' + latitude + ',' + longitude + '\n'
                fp.write(line)
        fp.close()

    def readBusStopFromLta(self):   # read busstop.json file to a dict: self.busStops_lta
        busstopsraw = readWriteFile().readF(self.ltaDataFileName)
        busstops = {}
        for abusstop in busstopsraw:
            busstopnumber = abusstop['BusStopCode']
            busstopdescription = [
                abusstop['Description'],
                abusstop['RoadName']
            ]
            busstoplocation = [
                abusstop['Latitude'],
                abusstop['Longitude']
            ]
            busstops[busstopnumber] = [busstopdescription,busstoplocation]
        return busstops

    def readBusStops(self):
        a = {}
        for busstopnumber, busstopdetails in self.busStops_lta.iteritems():
            if (busstopdetails[1][0] == 0 or busstopdetails[1][1] == 0):
                continue
            else:
                a[busstopnumber] = busstopdetails
                sn = busstopdetails[0][1]
                if sn in self.streetName:
                    a[busstopnumber][0].append(self.streetName[sn])
                else:
                    a[busstopnumber][0].append('')
        return a

    def readStreetName(self):
        fname = dataFolder.inputData + 'busstop_chinese.xlsx'
        xl_workbook = xlrd.open_workbook(os.path.expanduser(fname))
        xl_sheet = xl_workbook.sheet_by_index(0)
        num_cols = xl_sheet.ncols
        streets = []
        for row_idx in range(0, xl_sheet.nrows):
            astreet = []
            for col_idx in range(0, num_cols):
                astreet.append(xl_sheet.cell(row_idx, col_idx).value)
            streets.append(astreet)
        streets.pop(0)
        streetname = {}
        for astreet in streets:
            sname = astreet[2]
            sname_chn = astreet[4]
            if sname in streetname:
                continue
            else:
                streetname[sname] = sname_chn
        return streetname

class Mrt:
    Mrts = {}    #dict, mrtnumber:[mrtname,latitude,longitude]
    def __init__(self):
        self.Mrts = self.readMrtStations()

    def readMrtStations(self):
        # read MRT station information from excel file
        fname = dataFolder.inputData + 'MRT.xlsx'
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
            mrtlatitude = amrt[3]
            mrtlongitude = amrt[4]
            mrtdict[mrtnumber] = [mrtname, mrtlatitude, mrtlongitude, mrtname_chn]
        return mrtdict

class Mall:
    malls = {}
    def __init__(self):
        self.malls = self.readMall()

    def readMall(self):
        # read MRT station information from excel file
        fname = dataFolder.inputData +'Shopping Mall.xlsx'
        xl_workbook = xlrd.open_workbook(os.path.expanduser(fname))
        xl_sheet = xl_workbook.sheet_by_index(0)
        num_cols = xl_sheet.ncols
        mall = []
        for row_idx in range(0, xl_sheet.nrows):
            amall = []
            for col_idx in range(0, num_cols):
                amall.append(xl_sheet.cell(row_idx, col_idx).value)
            mall.append(amall)
        mall.pop(0)
        malldict = {}
        for amall in mall:
            mallname = amall[1]
            malllatitude = amall[2]
            malllongitude = amall[3]
            mallpostcode = amall[4]
            mallstreet = amall[5]
            mallweb = amall[6]
            malltel = amall[7]
            malldict[mallname] = [
                    malllatitude,
                    malllongitude,
                    mallpostcode,
                    mallstreet,
                    mallweb,
                    malltel]
        return malldict

class processData:

    def checkBusstopInBusLine(self, busstopnumber, buslinedetails):
        for abusstop in buslinedetails:
            if abusstop[0] == busstopnumber:
                return True
        return False

    def checkdistance(self, lat1, long1, lat2, long2, condition):
        p1 = (lat1,long1)
        p2 = (lat2,long2)
        return  vincenty(p1,p2).m < condition

    def findBusesAtBusStop(self, busstopnumber, buslines):
        a = []
        for buslinenumber, buslinedetails in buslines.iteritems():
            if self.checkBusstopInBusLine(busstopnumber, buslinedetails):
                a.append(buslinenumber)
        sorta = natsorted(a, key=lambda y: y.lower())
        info = 'The bus in ' + busstopnumber + ' are:'
        for onebus in sorta:
            info = info + onebus + ','
        if info.endswith(','):
            info = info[:-1]
        return info

    def processBusStop(self):
        busstops = busStop('').busStops
        buslines = busRoute('').busRoutes
        Mrts = Mrt().Mrts
        Malls = Mall().malls
        t = busstops
        for busstopnumber,busstopdetails in busstops.iteritems():
            info = self.findBusesAtBusStop(busstopnumber, buslines)
            b = []
            for mrtstationnumber, mrtstationdetails in Mrts.iteritems():
                if self.checkdistance(busstopdetails[1][0],busstopdetails[1][1],
                                      mrtstationdetails[1],mrtstationdetails[2],
                                      distance.DistanceMrtBusstation):
                    b.append(mrtstationnumber)
            c = []
            for mallname, malldetails in Malls.iteritems():
                if self.checkdistance(busstopdetails[1][0],busstopdetails[1][1],
                                      malldetails[0],malldetails[1],
                                      distance.DistanceMallBusstation):
                    c.append(mallname)
            t[busstopnumber].append(info)
            t[busstopnumber].append(b)
            t[busstopnumber].append(c)
        f = dataFolder.data + 'busstopsforapps.json'
        readWriteFile().saveF(f,t)

    def processmrt(self):
        # process MRT station information and save to json file
        busstops = busStop('').busStops
        Mrts = Mrt().Mrts
        Malls = Mall().malls
        t = Mrts
        for mrtnumber, mrtdetails in Mrts.iteritems():
            latMrt = mrtdetails[1]
            longMrt = mrtdetails[2]
            a = []
            for busstopnumber, busstopdetails in busstops.iteritems():
                latBusstation = busstopdetails[1][0]
                longBusstation = busstopdetails[1][1]
                if self.checkdistance(latMrt,longMrt,latBusstation,longBusstation, distance.DistanceMrtBusstation):
                    a.append(busstopnumber)
            b = []
            for mallname, malldetails in Malls.iteritems():
                latMall = malldetails[0]
                longMall = malldetails[1]
                if self.checkdistance(latMrt,longMrt,latMall,longMall,distance.DistanceMrtMall):
                    b.append(mallname)
            t[mrtnumber] = [t[mrtnumber],a,b]
        f1 = dataFolder.data + 'mrtforapps.json'
        readWriteFile().saveF(f1,t)

    def processmall(self):
        busstops = busStop('').busStops
        Mrts = Mrt().Mrts
        Malls = Mall().malls
        t = Malls
        for mallname, malldetails in Malls.iteritems():
            a = []
            latMall = malldetails[0]
            longMall = malldetails[1]
            for busstopnumber, busstopdetails in busstops.iteritems():
                latBusstop = busstopdetails[1][0]
                longBusstop = busstopdetails[1][1]
                if self.checkdistance(latMall,longMall,latBusstop,longBusstop,distance.DistanceMallBusstation):
                    a.append(busstopnumber)
            b = []
            for mrtname, mrtdetails in Mrts.iteritems():
                latMrt = mrtdetails[1]
                longMrt = mrtdetails[2]
                if self.checkdistance(latMall,longMall,latMrt,longMrt,distance.DistanceMrtMall):
                    b.append(mrtname)
            t[mallname] = [t[mallname], a , b]
        f = dataFolder.data + 'mallforapps.json'
        readWriteFile().saveF(f,t)
    #
    # def readstreetChnName(self):
    #     fname = self.inputdatafolder + 'busstop_chinese.xlsx'
    #     xl_workbook = xlrd.open_workbook(os.path.expanduser(fname))
    #     xl_sheet = xl_workbook.sheet_by_index(0)
    #     num_cols = xl_sheet.ncols
    #     streets = []
    #     for row_idx in range(0, xl_sheet.nrows):
    #         astreet = []
    #         for col_idx in range(0, num_cols):
    #             astreet.append(xl_sheet.cell(row_idx, col_idx).value)
    #         streets.append(astreet)
    #     streets.pop(0)
    #     streetname = {}
    #     for astreet in streets:
    #         sname = astreet[2]
    #         sname_chn = astreet[4]
    #         if sname in streetname:
    #             continue
    #         else:
    #             streetname[sname] = sname_chn
    #     return streetname




a = lta()