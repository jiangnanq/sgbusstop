__author__ = 'Jiang'
import json
import unicodedata
from geopy.distance import vincenty
# Class to process busstop/mall/mrt station/taxi stop information
# All information should been extract from LTA and saved to file
#
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
        with open(filename) as datafile:
            data=json.load(datafile)
        return data
    def readbusstopdynamic(self):
        busstopsraw=self.readF('data\\busstopdynamic.json')
        busstops=[]
        for abusstop in busstopsraw:
            busstopnumber=abusstop['Code']
            busstopdescription=[abusstop['Description'],abusstop['Road']]
            abusstopdetails={busstopnumber:busstopdescription}
            busstops.append(abusstopdetails)
        return busstops
    def readbusstopstatic(self):
        busstopsraw=self.readF('data\\busstopStatic.json')["features"]
        busstops=[]
        for abusstop in busstopsraw:
            # print abusstop['properties']['BUS_STOP_N']
            busstopnumber=abusstop['properties']['BUS_STOP_N']
            busroofnumber=abusstop['properties']['BUS_ROOF_N']
            buslocation=abusstop['properties']['LOC_DESC']
            buslatitude=abusstop['geometry']['coordinates'][0]
            buslongitude=abusstop['geometry']['coordinates'][1]
            busstopdescription=[busroofnumber,buslocation,buslatitude,buslongitude]
            busstopdetails={busstopnumber:busstopdescription}
            busstops.append(busstopdetails)
        return busstops
    def readbusroute(self):
        busrouteraw=self.readF('data\\sbsbusroute.json')
        busroute=[]
        for abusroute in busrouteraw:
            buscode=abusroute['SR_BS_CODE']

    def combinebusstopinfo(self):
    # combine bus stop information from
    # busstopgps.json static busstop information file with gps
    # sbsbusroute.json sbs bus stop with bus information
    # smrtbusroute.json smrt bus stop with bus information
    #     busstopwithgps=self.readF('data\\busstopStatic.json')['features']

        busstoproute=self.readF('data\\sbsbusroute.json')
        for abusstop in busstoproute:
            busstopnumber=abusstop['SR_BS_CODE']

        return busstopnumber
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


