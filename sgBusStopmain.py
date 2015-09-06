__author__ = 'Jiang'
from lta import *
from processdata import *
from geopy.distance import vincenty
import json

# busstop=lta('smrtbusservice')
# busstop=lta('sbsbusservice')
# busstop=lta('smrtbusroute')
# busstop=lta('sbsbusroute')
# busstop=lta('busstop')
# busstop.readDataFromLTA()

test=processdata().combinebusstopinfo()
<<<<<<< HEAD
print 'process completed'
=======
print 'process completed'
>>>>>>> 7886f10c5a21ef8824dcc568deb0f852dd8228a0
