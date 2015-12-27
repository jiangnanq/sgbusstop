import json
import os
# import unicodedata
from geopy.distance import vincenty
import xlrd
__author__ = 'Nanqing'
# Class to process busstop/mall/mrt station information
# All information should been extract
# from LTA and saved to file in the data directory


class processdata:
    datafolder = '~/Dropbox/project/busstoppy/data/'
    inputdatafolder = '~/Dropbox/project/busstoppy/inputdata/'

    def readF(self, filename):
        # read json file
        with open(os.path.expanduser(filename)) as datafile:
            data = json.load(datafile)
        return data

    def readbusstopdynamic(self):
        # read dynamic bus stop data,
        # dynamic data means read from LTA by GET method
        busstopsraw = self.readF(self.datafolder+'busstopdynamic.json')
        busstops = {}
        for abusstop in busstopsraw:
            busstopnumber = abusstop['Code']
            busstopdescription = [
                abusstop['Description'],
                abusstop['Road'],
                abusstop['BusStopCodeID']]
            busstops[busstopnumber] = busstopdescription
        return busstops

    def readbusstopstatic(self):
        # read static bus stop data,
        # static data means download data from datamall website
        busstopsraw = self.readF(self.datafolder+'busstopStatic.json')["features"]
        busstops = {}
        for abusstop in busstopsraw:
            busstopnumber = abusstop['properties']['BUS_STOP_N']
            busroofnumber = abusstop['properties']['BUS_ROOF_N']
            buslocation = abusstop['properties']['LOC_DESC']
            buslatitude = abusstop['geometry']['coordinates'][0]
            buslongitude = abusstop['geometry']['coordinates'][1]
            busstopdescription = [
                busroofnumber,
                buslocation,
                buslatitude,
                buslongitude]
            busstops[busstopnumber] = busstopdescription
        return busstops

    def readbusroute(self):
        # read bus route data
        busrouteraw = self.readF(self.datafolder+'sbsbusroute.json')
        busroute = []
        for abusroute in busrouteraw:
            buscode = abusroute['SR_BS_CODE']
            busnumber = abusroute['SR_SVC_NUM']
            busdistance = abusroute['SR_DISTANCE']
            busdirection = abusroute['SR_SVC_DIR']
            busrouteseq = abusroute['SR_ROUT_SEQ']
            busroutedetails = [
                buscode,
                busnumber,
                busdistance,
                busdirection,
                busrouteseq]
            busroute.append(busroutedetails)
        busrouterawsmrt = self.readF(self.datafolder+'smrtbusroute.json')
        for abusroute in busrouterawsmrt:
            buscode = abusroute['SR_BS_CODE']
            busnumber = abusroute['SR_SVC_NUM']
            busdistance = abusroute['SR_DISTANCE']
            busdirection = abusroute['SR_SVC_DIR']
            busrouteseq = abusroute['SR_ROUT_SEQ']
            busroutedetails = [
                buscode,
                busnumber,
                busdistance,
                busdirection,
                busrouteseq]
            busroute.append(busroutedetails)
        return busroute

    def processbusroute(self):
        # process bus route data from LTA data file
        # comibne bus stop information to each bus line
        busroute = self.readbusroute()
        buslines = {}
        for abusroute in busroute:
            atag = abusroute[0]+':'+abusroute[2]+':'+abusroute[3]+':'+abusroute[4]
            if abusroute[1] in buslines:
                busline = buslines[abusroute[1]]
                busline = busline+','+atag
                buslines[abusroute[1]] = busline    
            else:
                buslines[abusroute[1]] = atag
        f1 = self.datafolder+'busline.json'
        with open(os.path.expanduser(f1), 'w+') as fp:
            json.dump(buslines, fp)
        return buslines

    def combinebusstopinfo(self):
        # generate bus stop detail information
        # inlcude dyanmic,static and bus line information
        staticbusstops = self.readbusstopstatic()
        dynamicbusstops = self.readbusstopdynamic()
        busroutes = self.readbusroute()
        busstops = {}
        for abusstop in staticbusstops.keys():
            if abusstop in dynamicbusstops:
                staticbusstop = staticbusstops[abusstop]
                dynamicbusstop = dynamicbusstops[abusstop]
                busstoproofnumber = staticbusstop[0]
                # busstoplocation = staticbusstop[1]
                busstoplatitude = staticbusstop[2]
                busstoplongitude = staticbusstop[3]

                busstopdescription = dynamicbusstop[0]
                busstoproad = dynamicbusstop[1]
                busstopID = dynamicbusstop[2]

                busstoptag1 = [busstopdescription, busstoproad, busstopID]
                busstoptag2 = [busstoplatitude, busstoplongitude]
                busstoptag3 = busstoproofnumber
                busstops[abusstop] = [busstoptag1, busstoptag2, busstoptag3]
        for abusroute in busroutes:
            if abusroute[0] in busstops:
                if len(busstops[abusroute[0]]) == 3:
                    abus = []
                    abus.append(abusroute[1])
                    busstops[abusroute[0]].append(abus)
                else:
                    if abusroute[1] in busstops[abusroute[0]][3]:
                        continue
                    else:
                        busstops[abusroute[0]][3].append(abusroute[1])
        for key, abusstop in busstops.iteritems():
            if len(abusstop) == 4:
                busstoptext = 'The bus in '+key+' are:'
                abusstop[3].sort()
                for busline in abusstop[3]:
                    busstoptext = busstoptext+busline+','
                abusstop.pop()
                abusstop.append(busstoptext)
        print 'Start processing mrt&mall data!'
        malls = self.readF(self.datafolder+'mall.json')
        mrts = self.readF(self.datafolder+'mrt.json')
        for busstopkey, abusstop in busstops.iteritems():
            busstoplatitude = abusstop[1][1]
            busstoplongitude = abusstop[1][0]
            busstopcoordinate = (busstoplatitude, busstoplongitude)
            cloestmrt = []
            cloestmall = []
            for mrtkey, amrt in mrts.iteritems():
                mrtlatitude = amrt[0][1]
                mrtlongitude = amrt[0][2]
                mrtcoordinate = (mrtlatitude, mrtlongitude)
                if(vincenty(mrtcoordinate, busstopcoordinate).m < 300):
                    cloestmrt.append(mrtkey)
            for mallkey, amall in malls.iteritems():
                malllatitude = amall[0][0]
                malllongitude = amall[0][1]
                mallcoordinate = (malllatitude, malllongitude)
                if(vincenty(mallcoordinate, busstopcoordinate).m < 150):
                    cloestmall.append(mallkey)
            abusstop.append(cloestmall)
            abusstop.append(cloestmrt)
        f1 = self.datafolder + 'busstop.json'
        with open(os.path.expanduser(f1), 'w') as fp:
            json.dump(busstops, fp)
        return busstops

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
        return mrt

    def processmrt(self):
        # process MRT station information and save to json file
        print 'start processing mrt data.'
        mrt = self.readmrtdata()
        mrtdict = {}
        for amrt in mrt:
            mrtnumber = str(amrt[0])
            mrtname = amrt[1]
            mrtlatitude = amrt[3]
            mrtlongitude = amrt[4]
            mrtdict[mrtnumber] = [mrtname, mrtlatitude, mrtlongitude]
        busstops = self.readF(self.datafolder+"busstop.json")
        malls = self.readF(self.datafolder+"mall.json")
        for mrtkey, amrt in mrtdict.iteritems():
            mrtlatitude = amrt[1]
            mrtlongitude = amrt[2]
            mrtcoordinate = (mrtlatitude, mrtlongitude)
            closestbusstop = []
            closestmall = []
            for busstopkey, abusstop in busstops.iteritems():
                busstoplatitude = abusstop[1][1]
                busstoplongitude = abusstop[1][0]
                busstopcoordinate = (busstoplatitude, busstoplongitude)
                if(vincenty(mrtcoordinate, busstopcoordinate).m < 200):
                    closestbusstop.append(busstopkey)
            for mallkey, amall in malls.iteritems():
                malllatitude = amall[0][0]
                malllongitude = amall[0][1]
                mallcoordinate = (malllatitude, malllongitude)
                if(vincenty(mallcoordinate, mrtcoordinate).m < 300):
                    closestmall.append(mallkey)
            mrtdict[mrtkey] = [amrt, closestbusstop, closestmall]
        f1 = self.datafolder + 'mrt.json'
        with open(os.path.expanduser(f1), "w") as fp:
            json.dump(mrtdict, fp)
        return mrtdict

    def readmalldata(self):
        # read MRT station information from excel file
        fname = self.inputdatafolder+'Shopping Mall.xlsx'
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
        return mrt

    # process Shopping mall information and save to json file
    def processmalldata(self):
        print 'start processing.'
        mall = self.readmalldata()
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
        busstops = self.readF(self.datafolder+'busstop.json')
        mrts = self.readF(self.datafolder+'mrt.json')
        for mallkey, amall in malldict.iteritems():
            malllatitude = amall[0]
            malllongitude = amall[1]
            mallcoordinate = (malllatitude, malllongitude)
            closestbusstop = []
            cloesetmrt = []
            for busstopkey, abusstop in busstops.iteritems():
                busstoplatitude = abusstop[1][1]
                busstoplongitude = abusstop[1][0]
                busstopcoordinate = (busstoplatitude, busstoplongitude)
                if(vincenty(mallcoordinate, busstopcoordinate).m < 150):
                    closestbusstop.append(busstopkey)
            for mrtkey, amrt in mrts.iteritems():
                mrtlatitude = amrt[0][1]
                mrtlongitude = amrt[0][2]
                mrtcoordinate = (mrtlatitude, mrtlongitude)
                if(vincenty(mallcoordinate, mrtcoordinate).m < 300):
                    cloesetmrt.append(mrtkey)
            malldict[mallkey] = [amall, closestbusstop, cloesetmrt]
        f1 = self.datafolder + 'mall.json'
        print 'Start to write to file.'
        with open(os.path.expanduser(f1), "w") as fp:
            json.dump(malldict, fp)
        return malldict
