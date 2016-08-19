import json
import os
from geopy.distance import vincenty
import xlrd
from natsort import natsorted, ns
__author__ = 'Nanqing'
# Class to process busstop/mall/mrt station information
# All information should been extract
# from LTA and saved to file in the data directory

class processdata:
    datafolder = '~/Dropbox/project/busstoppy/data/'
    inputdatafolder = '~/Dropbox/project/busstoppy/inputdata/'
    DistanceMrtBusstation = 150
    DistanceMrtMall = 300
    DistanceMallBusstation = 150
    busstops_lta = {}        #dict, busstopnumber: [description, roadname], [latitude, longitude]
    mrtSource = {}          #dict, mrtnumber:[mrtname,latitude,longitude]
    mallSource = {}         #dict, mallname:[latitude,longitude,....]
    buslines = {}           #dict, busnumber:[busstopnumber, distance, direction, sequence]
    busstops = {}           #dict , filter  lta data, remove busstop without location info
    streetname = {}         #dict, streetname_eng: streetname_chn

    def __init__(self):
        self.busstops_lta = self.readbusstoplta()
        self.streetname = self.readstreetChnName()
        self.mrtSource = self.readmrtdata()
        self.mallSource = self.readmalldata()
        self.buslines = self.readbusline()
        self.busstops = self.readbusstops()

    def readF(self, filename):
        # read json file
        with open(os.path.expanduser(filename)) as datafile:
            data = json.load(datafile)
        return data

    def saveF(self, filename, datatosave):
        with open(os.path.expanduser(filename), 'w') as fp:
            json.dump(datatosave, fp)

    def readbusstoplta(self):
        busstopsraw = self.readF(self.datafolder + 'busstop.json')
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
    #filter busstops, remove busstops without location information, add Chinese street name
    def readbusstops(self):
        a = {}
        for busstopnumber, busstopdetails in self.busstops_lta.iteritems():
            if (busstopdetails[1][0] == 0 or busstopdetails[1][1] == 0):
                continue
            else:
                a[busstopnumber] = busstopdetails
                sn = busstopdetails[0][1]
                if sn in self.streetname:
                    a[busstopnumber][0].append(self.streetname[sn])
                else:
                    a[busstopnumber][0].append('')
        return a

    def readbusline(self):
        buslineraw = self.readF(self.datafolder + 'busline.json')
        allbuslines = {}
        for key, value in buslineraw.iteritems():
            a = []
            allstops = value.split(',')
            for eachStops in allstops:
                aStop = eachStops.split(':')
                a.append(aStop)
            allbuslines[key] = a
        return allbuslines

    def processbusroutes(self):
        # process bus routes from LTA data
        # Generate data to busline.json
        busStopOfRoutes_lta = self.readF(self.datafolder + 'busroutes.json')
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
        f1 = self.datafolder + 'busline.json'
        self.saveF(f1, busroutes)
        return


    def checkBusstopInBusLine(self,busstopnumber, buslinenumber):
        for abusstop in self.buslines[buslinenumber]:
            if abusstop[0] == busstopnumber:
                return True
        return False

    def checkdistance(self, lat1, long1, lat2, long2, condition):
        p1 = (lat1,long1)
        p2 = (lat2,long2)
        return  vincenty(p1,p2).m < condition

    def processBusStop(self):
        t = self.busstops
        for busstopnumber,busstopdetails in self.busstops.iteritems():
            a = []
            for buslinenumber, busline in self.buslines.iteritems():
                if self.checkBusstopInBusLine(busstopnumber,buslinenumber):
                    a.append(buslinenumber)
            sorta = natsorted(a, key=lambda y:y.lower())
            info = 'The bus in ' + busstopnumber + ' are:'
            for onebus in sorta:
                info = info + onebus + ','
            if info.endswith(','):
                info = info[:-1]
            b = []
            for mrtstationnumber, mrtstationdetails in self.mrtSource.iteritems():
                if self.checkdistance(busstopdetails[1][0],busstopdetails[1][1],
                                      mrtstationdetails[1],mrtstationdetails[2],
                                      self.DistanceMrtBusstation):
                    b.append(mrtstationnumber)
            c = []
            for mallname, malldetails in self.mallSource.iteritems():
                if self.checkdistance(busstopdetails[1][0],busstopdetails[1][1],
                                      malldetails[0],malldetails[1],
                                      self.DistanceMallBusstation):
                    c.append(mallname)
            t[busstopnumber] = [t[busstopnumber], info, b, c]
        f = self.datafolder + 'busstopsforapps.json'
        self.saveF(f,t)

    def checkBusStops(self):
        a = []
        for busstopnumber, busstopdetails in self.busstops_lta.iteritems():
            if (busstopdetails[1][0] == 0 or busstopdetails[1][1] == 0):
                a.append(busstopnumber)
        return  a

    def checkBusLines(self):
        for amissbusstop in self.checkBusStops():
            for busnumber,abusline in self.buslines.iteritems():
                for abusstop in abusline:
                    if (abusstop[0] == amissbusstop):
                        print busnumber, amissbusstop


    def readmrtdata(self):
        # read MRT station information from excel file
        fname = self.inputdatafolder+'MRT.xlsx'
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

    def processmrt(self):
        # process MRT station information and save to json file
        t = self.mrtSource
        mrt = self.readmrtdata()
        for mrtnumber, mrtdetails in mrt.iteritems():
            latMrt = mrtdetails[1]
            longMrt = mrtdetails[2]
            a = []
            for busstopnumber, busstopdetails in self.busstops.iteritems():
                latBusstation = busstopdetails[1][0]
                longBusstation = busstopdetails[1][1]
                if self.checkdistance(latMrt,longMrt,latBusstation,longBusstation, self.DistanceMrtBusstation):
                    a.append(busstopnumber)
            b = []
            for mallname, malldetails in self.mallSource.iteritems():
                latMall = malldetails[0]
                longMall = malldetails[1]
                if self.checkdistance(latMrt,longMrt,latMall,longMall,self.DistanceMrtMall):
                    b.append(mallname)
            t[mrtnumber] = [t[mrtnumber],a,b]
        f1 = self.datafolder + 'mrtforapps.json'
        self.saveF(f1,t)

    def readmalldata(self):
        # read MRT station information from excel file
        fname = self.inputdatafolder+'Shopping Mall.xlsx'
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

    # process Shopping mall information and save to json file
    def processmalldata(self):
        t = self.mallSource
        for mallname, malldetails in self.mallSource.iteritems():
            a = []
            latMall = malldetails[0]
            longMall = malldetails[1]
            for busstopnumber, busstopdetails in self.busstops.iteritems():
                latBusstop = busstopdetails[1][0]
                longBusstop = busstopdetails[1][1]
                if self.checkdistance(latMall,longMall,latBusstop,longBusstop,self.DistanceMallBusstation):
                    a.append(busstopnumber)
            b = []
            for mrtname, mrtdetails in self.mrtSource.iteritems():
                latMrt = mrtdetails[1]
                longMrt = mrtdetails[2]
                if self.checkdistance(latMall,longMall,latMrt,longMrt,self.DistanceMrtMall):
                    b.append(mrtname)
            t[mallname] = [t[mallname], a , b]
        f = self.datafolder + 'mallforapps.json'
        self.saveF(f,t)

    def readstreetChnName(self):
        fname = self.inputdatafolder + 'busstop_chinese.xlsx'
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

