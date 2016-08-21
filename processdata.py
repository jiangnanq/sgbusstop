import json
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

    def __init__(self, type):
        # init class base on the appoint class type
        self.headers = {
            'AccountKey': self.AccountKey,
            'UniqueUserID': self.UniqueUserID,
            'accept': 'application/json'}
        self.path = self.ltatype[type]

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

class dataFolder:
    data = '~/Dropbox/project/busstoppy/data/'
    inputData = '~/Dropbox/project/busstoppy/inputdata/'

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
    ltaDataFile = dataFolder.data + 'busRoutesLta.json'
    localDataFile = dataFolder.data + 'busline.json'
    busRoutes = {}  #dict, busnumber:[busstopnumber, distance, direction, sequence],......
    def __init__(self, type):
        if type == 'lta':
            self.readBusRoutesFromLta()
        else:
            self.busRoutes = self.readBusRoutes()

    def readBusRoutesFromLta(self):
        readWriteFile().saveF(self.ltaDataFile, lta(ltatype.busroute).readDataFromLTA())

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
    ltaDataFileName = dataFolder.data + 'busstop'
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
        readWriteFile().saveF(self.ltaDataFileName,lta(ltatype.busstop).readDataFromLTA())

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
        sorta = natsorted(a, key=lambda  y:y.lower())
        info = 'The bus in ' + busstopnumber + ' are: '
        for onebus in sorta:
            info = info + onebus + ','
        if info.endswith(','):
            info = info[:-1]
        return  info

    def processBusStop(self):
        busstops = busStop().busStops
        buslines = busRoute().busRoutes
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
            t[busstopnumber] = [t[busstopnumber], info, b, c]
        f = dataFolder.data + 'busstopsforapps.json'
        readWriteFile().saveF(f,t)

    def processmrt(self):
        # process MRT station information and save to json file
        busstops = busStop().busStops
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
        busstops = busStop().busStops
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

