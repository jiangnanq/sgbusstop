__author__ = 'Jiang'
from lta import *
from processdata import *
# from process import processdata
from geopy.distance import vincenty
import json

# busstop=lta('smrtbusservice')
# busstop=lta('sbsbusservice')
# busstop=lta('smrtbusroute')
# busstop=lta('sbsbusroute')
# busstop=lta('busstop')
# busstop.readDataFromLTA()
# test=processdata().readbusstopdynamic()
test=processdata().readbusstopstatic()
# print test


# with open('data\smrtbusroute.json') as datafile:
#     data=json.load(datafile)
# jsonObj=busstop.GetDataFromLta('100')
# with open('test.json','w') as outputfile:
#    json.dump(jsonObj,outputfile,sort_keys=True,indent=4,ensure_ascii=False)
# test=processdata('BusStopDetails')
# print 'mall'
# result1=test.checkTargetwithinRange('busstop','mall',150)
# print 'mrt'
# result2=test.checkTargetwithinRange('busstop','mrt',150)
# print 'taxistop'
# result3=test.checkTargetwithinRange('busstop','taxistop',150)
# result={}
# for item in test.busstoplist:
#     result[item]=test.busstoplist[item],result1[item],result2[item],result3[item]
#     #print result[item]
# with open('busstop1.json','w') as outputfile:
#     json.dump(result,outputfile,sort_keys=True,indent=4,ensure_ascii=False)
print 'process completed'