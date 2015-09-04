__author__ = 'Jiang'
from lta import *
from processdata import *
from geopy.distance import vincenty
import json

# busstop=lta('smrtbusservice')
busstop=lta('sbsbusservice')
# busstop=lta('smrtbusroute')
# busstop=lta('sbsbusroute')
# busstop=lta('busstop')
busstop.readDataFromLTA()

# test=processdata().processmrt()
print 'process completed'