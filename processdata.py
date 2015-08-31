__author__ = 'Jiang'
import json
import unicodedata
from geopy.distance import vincenty
import xlrd
# Class to process busstop/mall/mrt station/taxi stop information
# All information should been extract from LTA and saved to file
class processdata:
    filename='BusStopDetails'
    busstoplist={}
    malllist={}
    mrtlist={}
    taxistoplist={}
    # def __init__(self,filename):
    #     self.filename=filename
    #     # self.readDataFromJson()
    #     # print 'busstoplist:',len(self.busstoplist.keys())
    #     #print 'malllist:',len(self.malllist.keys())
    #     #print 'mrtlist:',len(self.mrtlist.keys())
    #     #print 'taxistoplist:',len(self.taxistoplist.keys())
    def readF(self,filename):
        #read json file
        with open(filename) as datafile:
            data=json.load(datafile)
        return data
    def readbusstopdynamic(self):
        #read dynamic bus stop data
        busstopsraw=self.readF('data\\busstopdynamic.json')
        busstops={}
        for abusstop in busstopsraw:
            busstopnumber=abusstop['Code']
            busstopdescription=[abusstop['Description'],abusstop['Road'],abusstop['BusStopCodeID']]
            busstops[busstopnumber]=busstopdescription
        return busstops
    def readbusstopstatic(self):
        #read static bus stop data
        busstopsraw=self.readF('data\\busstopStatic.json')["features"]
        busstops={}
        for abusstop in busstopsraw:
            # print abusstop['properties']['BUS_STOP_N']
            busstopnumber=abusstop['properties']['BUS_STOP_N']
            busroofnumber=abusstop['properties']['BUS_ROOF_N']
            buslocation=abusstop['properties']['LOC_DESC']
            buslatitude=abusstop['geometry']['coordinates'][0]
            buslongitude=abusstop['geometry']['coordinates'][1]
            busstopdescription=[busroofnumber,buslocation,buslatitude,buslongitude]
            busstops[busstopnumber]=busstopdescription
        return busstops
    def readbusroute(self):
        #read bus route data
        busrouteraw=self.readF('data\\sbsbusroute.json')
        busroute=[]
        for abusroute in busrouteraw:
            buscode=abusroute['SR_BS_CODE']
            busnumber=abusroute['SR_SVC_NUM']
            busdistance=abusroute['SR_DISTANCE']
            busdirection=abusroute['SR_SVC_DIR']
            busrouteseq=abusroute['SR_ROUT_SEQ']
            busroutedetails=[buscode,busnumber,busdistance,busdirection,busrouteseq]
            busroute.append(busroutedetails)
        busrouterawsmrt=self.readF('data\\smrtbusroute.json')
        for abusroute in busrouterawsmrt:
            buscode=abusroute['SR_BS_CODE']
            busnumber=abusroute['SR_SVC_NUM']
            busdistance=abusroute['SR_DISTANCE']
            busdirection=abusroute['SR_SVC_DIR']
            busrouteseq=abusroute['SR_ROUT_SEQ']
            busroutedetails=[buscode,busnumber,busdistance,busdirection,busrouteseq]
            busroute.append(busroutedetails)
        return busroute
    def processbusroute(self):
        #process bus rote data from LTA data file
        busroute=self.readbusroute()
        buslines={}
        for abusroute in busroute:
            atag=abusroute[0]+':'+abusroute[2]+':'+abusroute[3]+':'+abusroute[4]
            if abusroute[1] in buslines:
                busline=buslines[abusroute[1]]
                busline=busline+','+atag
                buslines[abusroute[1]]=busline
            else:
                buslines[abusroute[1]]=atag
        with open('busline.json','w') as fp:
            json.dump(buslines,fp)
        return buslines
    def combinebusstopinfo(self):
        #generate bus stop detail information
        staticbusstops=self.readbusstopstatic()
        dynamicbusstops=self.readbusstopdynamic()
        busroutes=self.readbusroute()
        busstops={}
        for abusstop in staticbusstops.keys():
            if abusstop in dynamicbusstops:
                staticbusstop=staticbusstops[abusstop]
                dynamicbusstop=dynamicbusstops[abusstop]
                busstoproofnumber=staticbusstop[0]
                busstoplocation=staticbusstop[1]
                busstoplatitude=staticbusstop[2]
                busstoplongitude=staticbusstop[3]

                busstopdescription=dynamicbusstop[0]
                busstoproad=dynamicbusstop[1]
                busstopID=dynamicbusstop[2]

                busstoptag1=[busstopdescription,busstoproad,busstopID,busstoplocation]
                busstoptag2=[busstoplatitude,busstoplongitude]
                busstoptag3=busstoproofnumber
                busstops[abusstop]=[busstoptag1,busstoptag2,busstoptag3]
        for abusroute in busroutes:
            if abusroute[0] in busstops:
                if len(busstops[abusroute[0]])==3:
                    abus=[]
                    abus.append(abusroute[1])
                    busstops[abusroute[0]].append(abus)
                else:
                    if abusroute[1] in busstops[abusroute[0]][3]:
                        continue
                    else:
                        busstops[abusroute[0]][3].append(abusroute[1])
        for key,abusstop in busstops.iteritems():
            if len(abusstop)==4:
                busstoptext='The bus in '+key+' are '
                for busline in abusstop[3]:
                    busstoptext=busstoptext+busline+','
                abusstop.pop()
                abusstop.append(busstoptext)
        with open('busstop.json','w') as fp:
            json.dump(busstops,fp)
        return busstops
    def  readmrtdata(self):
        fname='inputdata\\MRT.xlsx'
        xl_workbook=xlrd.open_workbook(fname)
        sheet_names=xl_workbook.sheet_names()
        xl_sheet=xl_workbook.sheet_by_index(0)
        row=xl_sheet.row(0)
        return row
    # def readDataFromJson(self):
    #     self.busstoplist= self.readF('BusStopDetails.json')
    #     self.malllist=self.readF('mall.json')
    #     self.mrtlist=self.readF('mrt.json')
    #     self.taxistoplist=self.readF('taxistoplist.json')
    # def coordinate(self,item,type):
    #     if type=='mrt':
    #         latitude=self.mrtlist[item][1]
    #         longitude=self.mrtlist[item][2]
    #     elif type=='mall':
    #         latitude=self.malllist[item][0]
    #         longitude=self.malllist[item][1]
    #     elif type=='taxistop':
    #         taxistopcoordinate=unicodedata.normalize('NFKD',self.taxistoplist[item][1]).encode('ascii','ignore')
    #         latitude=taxistopcoordinate.split(',')[0]
    #         longitude=taxistopcoordinate.split(',')[1]
    #     elif type=='busstop':
    #         latitude=self.busstoplist[item][1][1]
    #         longitude=self.busstoplist[item][1][0]
    #     return (latitude,longitude)
    # def checklisttype(self,type):
    #     if type=='mrt':
    #         return self.mrtlist
    #     elif type=='mall':
    #         return self.malllist
    #     elif type=='taxistop':
    #         return self.taxistoplist
    #     elif type=='busstop':
    #         return self.busstoplist
    # def checkTargetwithinRange(self,targetType,itemType,distance):
    #     target=self.checklisttype(targetType)
    #     item=self.checklisttype(itemType)
    #     result={}
    #     for targetItem in target:
    #         #print targetItem
    #         targetItemCoordinate=self.coordinate(targetItem,targetType)
    #         #print targetItemCoordinate
    #         resultItem=[]
    #         for aitem in item:
    #             itemCoordinate=self.coordinate(aitem,itemType)
    #             if((vincenty(targetItemCoordinate,itemCoordinate).m)<distance):
    #                 resultItem.append(aitem)
    #         result[targetItem]=resultItem
    #         #print target[targetItem],result[targetItem]
    #     return result


