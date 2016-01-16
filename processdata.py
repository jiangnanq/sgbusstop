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
    DistanceMrtBusstation = 150
    DistanceMrtMall = 300
    DistanceMallBusstation = 150

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
        busstopsraw = self.readF(self.inputdatafolder+'bus-stops.json')
        busstops = {}
        for abusstop in busstopsraw:
            busstopnumber = abusstop['no']
            latitude = abusstop['lat']
            longitude = abusstop['lng']
            name = abusstop['name']
            busstops[busstopnumber] = [latitude,longitude,name]
        # for abusstop in busstopsraw:
        #     busstopnumber = abusstop['properties']['BUS_STOP_N']
        #     busroofnumber = abusstop['properties']['BUS_ROOF_N']
        #     buslocation = abusstop['properties']['LOC_DESC']
        #     buslatitude = abusstop['geometry']['coordinates'][0]
        #     buslongitude = abusstop['geometry']['coordinates'][1]
        #     busstopdescription = [
        #         busroofnumber,
        #         buslocation,
        #         buslatitude,
        #         buslongitude]
        #     busstops[busstopnumber] = busstopdescription
        return busstops

    # def readbusroute(self):
    #     # read bus route data
    #     busrouteraw = self.readF(self.datafolder+'sbsbusroute.json')
    #     busroute = []
    #     for abusroute in busrouteraw:
    #         buscode = abusroute['SR_BS_CODE']
    #         busnumber = abusroute['SR_SVC_NUM']
    #         busdistance = abusroute['SR_DISTANCE']
    #         busdirection = abusroute['SR_SVC_DIR']
    #         busrouteseq = abusroute['SR_ROUT_SEQ']
    #         busroutedetails = [
    #             buscode,
    #             busnumber,
    #             busdistance,
    #             busdirection,
    #             busrouteseq]
    #         busroute.append(busroutedetails)
    #     busrouterawsmrt = self.readF(self.datafolder+'smrtbusroute.json')
    #     for abusroute in busrouterawsmrt:
    #         buscode = abusroute['SR_BS_CODE']
    #         busnumber = abusroute['SR_SVC_NUM']
    #         busdistance = abusroute['SR_DISTANCE']
    #         busdirection = abusroute['SR_SVC_DIR']
    #         busrouteseq = abusroute['SR_ROUT_SEQ']
    #         busroutedetails = [
    #             buscode,
    #             busnumber,
    #             busdistance,
    #             busdirection,
    #             busrouteseq]
    #         busroute.append(busroutedetails)
    #     return busroute

    # def processbusroute(self):
    #     # process bus route data from LTA data file
    #     # comibne bus stop information to each bus line
    #     # generate busline file
    #     busroute = self.readbusroute()
    #     buslines = {}
    #     for abusroute in busroute:
    #         atag = abusroute[0]+':'+abusroute[2]+':'+abusroute[3]+':'+abusroute[4]
    #         if abusroute[1] in buslines:
    #             busline = buslines[abusroute[1]]
    #             busline = busline+','+atag
    #             buslines[abusroute[1]] = busline    
    #         else:
    #             buslines[abusroute[1]] = atag
    #     f1 = self.datafolder+'busline.json'
    #     with open(os.path.expanduser(f1), 'w+') as fp:
    #         json.dump(buslines, fp)
    #     return buslines
    def allBusStops(self):
        # return a list of all busstops number
        a = []
        allBusRoutes = self.readF(self.datafolder + 'busline.json')
        for abus in allBusRoutes.keys():
            for abusstop in allBusRoutes[abus].split(','):
                a.append(abusstop.split(':')[0])
        allbusstops = sorted(set(a))
        return allbusstops

    def allBusRoutes(self):
        # return a dictonary of all bus routes
        return self.readF(self.datafolder + 'busline.json')
    def fillMissingBusStops(self,allbusroutes,busstops):
        # fill up missing busstops information base on the
        # previous bus stop information
        for key,abusline in allbusroutes.iteritems():
            for abusstop in abusline.split(','):
                busstopnumber = abusstop.split(':')[0]
                busstopname = busstops[busstopnumber][0][0]
                busstoplatitude = busstops[busstopnumber][1][0]
                if (busstopname != 'NA') and (busstoplatitude != 'NA'):
                    previousBusStopNumber = str(busstopnumber)
                    break
            for abusstop in abusline.split(','):
                abusstopnumber = str(abusstop.split(':')[0])
                if busstops[abusstopnumber][0][0] == 'NA':
                    print 'fill bustop ' + abusstopnumber + 'with' + previousBusStopNumber
                    busstops[abusstopnumber][0][0] = busstops[previousBusStopNumber][0][0]
                    busstops[abusstopnumber][0][1] = busstops[previousBusStopNumber][0][1]
                    busstops[abusstopnumber][0][2] = busstops[previousBusStopNumber][0][2]
                if busstops[abusstopnumber][1][0] == 'NA':
                    print 'fill bustop ' + abusstopnumber + 'with' + previousBusStopNumber
                    busstops[abusstopnumber][1][0] = busstops[previousBusStopNumber][1][0]
                    busstops[abusstopnumber][1][1] = busstops[previousBusStopNumber][1][1]
                previousBusStopNumber = abusstopnumber
        return busstops

    def combinebusstopinfo(self):
        # generate bus stop detail information
        # inlcude dyanmic,static and bus line information
        staticbusstops = self.readbusstopstatic()
        dynamicbusstops = self.readbusstopdynamic()
        allBusStops = self.allBusStops()
        allBusRoutes = self.allBusRoutes()
        busstops = {}
        for abusstop in allBusStops:
            businfo = 'The bus in ' + abusstop + 'are:'

            if abusstop in dynamicbusstops:
                dynamicbusstop = dynamicbusstops[abusstop]
                busstopdescription = dynamicbusstop[0]
                busstoproad = dynamicbusstop[1]
                busstopID = dynamicbusstop[2]
            else:
                busstopdescription = 'NA'
                busstoproad = 'NA'
                busstopID = 'NA'

            if abusstop in staticbusstops:
                staticbusstop = staticbusstops[abusstop]
                busstoplatitude = staticbusstop[0]
                busstoplongitude = staticbusstop[1]
            else:
                busstoplatitude = 'NA'
                busstoplongitude = 'NA'

            busstoptag1 = [busstopdescription, busstoproad, busstopID]
            busstoptag2 = [busstoplatitude, busstoplongitude]
            busAtCurrentStop = ''
            for key,value in allBusRoutes.iteritems():
                if abusstop in value:
                    busAtCurrentStop = busAtCurrentStop + key + ','
            busstops[abusstop] = [busstoptag1, busstoptag2, busAtCurrentStop]
        allbusstops = self.fillMissingBusStops(allBusRoutes,busstops)
        for key, abusstop in allbusstops.iteritems():
            abusstop[2] = 'The buses in '+ key + ' are:'+abusstop[2]
        # for abusroute in busroutes:
        #     if abusroute[0] in busstops:
        #         if len(busstops[abusroute[0]]) == 2:
        #             abus = []
        #             abus.append(abusroute[1])
        #             busstops[abusroute[0]].append(abus)
        #         else:
        #             if abusroute[1] in busstops[abusroute[0]][2]:
        #                 continue
        #             else:
        #                 busstops[abusroute[0]][2].append(abusroute[1])
        # for key, abusstop in busstops.iteritems():
        #     if len(abusstop) == 3:
        #         busstoptext = 'The bus in '+key+' are:'
        #         abusstop[2].sort()
        #         for busline in abusstop[2]:
        #             busstoptext = busstoptext+busline+','
        #         abusstop.pop()
        #         abusstop.append(busstoptext)
        #     else:
        #         abusstop.append('The bus in '+key+' are:')
        print 'Start processing mrt&mall data!'
        malls = self.readF(self.datafolder+'mall.json')
        mrts = self.readF(self.datafolder+'mrt.json')
        for busstopkey, abusstop in busstops.iteritems():
            busstoplatitude = abusstop[1][0]
            busstoplongitude = abusstop[1][1]
            busstopcoordinate = (busstoplatitude, busstoplongitude)
            cloestmrt = []
            cloestmall = []
            for mrtkey, amrt in mrts.iteritems():
                mrtlatitude = amrt[0][1]
                mrtlongitude = amrt[0][2]
                mrtcoordinate = (mrtlatitude, mrtlongitude)
                if(vincenty(mrtcoordinate, busstopcoordinate).m < self.DistanceMrtBusstation):
                    cloestmrt.append(mrtkey)
            for mallkey, amall in malls.iteritems():
                malllatitude = amall[0][0]
                malllongitude = amall[0][1]
                mallcoordinate = (malllatitude, malllongitude)
                if(vincenty(mallcoordinate, busstopcoordinate).m < self.DistanceMallBusstation):
                    cloestmall.append(mallkey)
            abusstop.append(cloestmall)
            abusstop.append(cloestmrt)
        f1 = self.datafolder + 'busstop.json'
        with open(os.path.expanduser(f1), 'w') as fp:
            json.dump(allbusstops, fp)
        return

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
                busstoplatitude = abusstop[1][0]
                busstoplongitude = abusstop[1][1]
                busstopcoordinate = (busstoplatitude, busstoplongitude)
                if(vincenty(mrtcoordinate, busstopcoordinate).m < self.DistanceMrtBusstation):
                    closestbusstop.append(busstopkey)
            for mallkey, amall in malls.iteritems():
                malllatitude = amall[0][0]
                malllongitude = amall[0][1]
                mallcoordinate = (malllatitude, malllongitude)
                if(vincenty(mallcoordinate, mrtcoordinate).m < self.DistanceMrtMall):
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
                busstoplatitude = abusstop[1][0]
                busstoplongitude = abusstop[1][1]
                busstopcoordinate = (busstoplatitude, busstoplongitude)
                if(vincenty(mallcoordinate, busstopcoordinate).m < self.DistanceMallBusstation):
                    closestbusstop.append(busstopkey)
            for mrtkey, amrt in mrts.iteritems():
                mrtlatitude = amrt[0][1]
                mrtlongitude = amrt[0][2]
                mrtcoordinate = (mrtlatitude, mrtlongitude)
                if(vincenty(mallcoordinate, mrtcoordinate).m < self.DistanceMrtMall):
                    cloesetmrt.append(mrtkey)
            malldict[mallkey] = [amall, closestbusstop, cloesetmrt]
        f1 = self.datafolder + 'mall.json'
        print 'Start to write to file.'
        with open(os.path.expanduser(f1), "w") as fp:
            json.dump(malldict, fp)
        return malldict

    def processSpecialBus(self):
        # Process special bus in the special bus file
        specialBusFileName = self.inputdatafolder + 'specialbus.txt'
        allbusstops = self.readF(self.datafolder + 'busstop.json')
        allbuslines = self.readF(self.datafolder + 'busline.json')
        with open(os.path.expanduser(specialBusFileName)) as datafile:
            for abus in datafile:
                busnumber = abus.partition(':')[0]
                busstops = abus.partition(':')[2].split(',')
                for i, abusstop in enumerate(busstops):
                    busstops[i] = abusstop.strip('\n')
                busstoplocation = []
                # update busstop.json for each special busline
                for abusstop in busstops:
                    latitude = allbusstops[abusstop][1][0]
                    longitude = allbusstops[abusstop][1][1]
                    busstoplocation.append((latitude,longitude))
                    test = allbusstops[abusstop][2]
                    allbusstops[abusstop][2] = test.replace(busnumber[0:3],busnumber)
                busstopdistance = []
                for i in range(len(busstoplocation)):
                    if i == 0 : 
                        busstopdistance.append("%.1f" % 0)
                    else:
                        dis = vincenty(busstoplocation[i],busstoplocation[i-1]).m+ float(busstopdistance[i-1])
                        busstopdistance.append("%.1f" % dis)
                for i, dis in enumerate(busstopdistance):
                    disFloat = float(dis) / 1000
                    busstopdistance[i] = "%.1f" % disFloat
                for i in range(len(busstops)):
                    busstops[i] = busstops[i] + ':' + busstopdistance[i] + ':' + '1' + ':' + str(i+1)
                    busline = ''
                for busstop in busstops:
                    busline = busline + busstop + ','
                busline = busline.rstrip(',')
                allbuslines[busnumber] = busline
                if busnumber[0:3] in allbuslines:
                    del allbuslines[busnumber[0:3]]
        f1 = self.datafolder+'busline.json'        
        with open(os.path.expanduser(f1), 'w') as fp:
            json.dump(allbuslines, fp)
        f1 = self.datafolder+'busstop.json'        
        with open(os.path.expanduser(f1), 'w') as fp:
            json.dump(allbusstops, fp)
