__author__ = 'Jiang'
import json
import unicodedata
from geopy.distance import vincenty
# To process busstop/mall/mrt station/taxi stop information
#
class processdata(object):
    filename='BusStopDetails'
    busstoplist={}
    malllist={}
    mrtlist={}
    taxistoplist={}
    def __init__(self,filename):
        self.filename=filename
        self.readDataFromJson()
        #print 'busstoplist:',len(self.busstoplist.keys())
        #print 'malllist:',len(self.malllist.keys())
        #print 'mrtlist:',len(self.mrtlist.keys())
        #print 'taxistoplist:',len(self.taxistoplist.keys())
    def readF(self,filename):
        with open(filename) as datafile:
            data=json.load(datafile)
        return data
    def readDataFromJson(self):
        self.busstoplist= self.readF('BusStopDetails.json')
        self.malllist=self.readF('mall.json')
        self.mrtlist=self.readF('mrt.json')
        self.taxistoplist=self.readF('taxistoplist.json')
    def coordinate(self,item,type):
        if type=='mrt':
            latitude=self.mrtlist[item][1]
            longitude=self.mrtlist[item][2]
        elif type=='mall':
            latitude=self.malllist[item][0]
            longitude=self.malllist[item][1]
        elif type=='taxistop':
            taxistopcoordinate=unicodedata.normalize('NFKD',self.taxistoplist[item][1]).encode('ascii','ignore')
            latitude=taxistopcoordinate.split(',')[0]
            longitude=taxistopcoordinate.split(',')[1]
        elif type=='busstop':
            latitude=self.busstoplist[item][1][1]
            longitude=self.busstoplist[item][1][0]
        return (latitude,longitude)
    def checklisttype(self,type):
        if type=='mrt':
            return self.mrtlist
        elif type=='mall':
            return self.malllist
        elif type=='taxistop':
            return self.taxistoplist
        elif type=='busstop':
            return self.busstoplist
    def checkTargetwithinRange(self,targetType,itemType,distance):
        target=self.checklisttype(targetType)
        item=self.checklisttype(itemType)
        result={}
        for targetItem in target:
            #print targetItem
            targetItemCoordinate=self.coordinate(targetItem,targetType)
            #print targetItemCoordinate
            resultItem=[]
            for aitem in item:
                itemCoordinate=self.coordinate(aitem,itemType)
                if((vincenty(targetItemCoordinate,itemCoordinate).m)<distance):
                    resultItem.append(aitem)
            result[targetItem]=resultItem
            #print target[targetItem],result[targetItem]
        return result


