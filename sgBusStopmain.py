from lta import *
from processdata import *
__author__ = 'Jiang'

# busstop = lta('smrtbusservice')
# busstop = lta('sbsbusservice')
# busstop = lta('smrtbusroute')
busstop = lta('sbsbusroute')
# busstop = lta('busstop')
busstop.readDataFromLTA()

# test=processdata().combinebusstopinfo()
print 'process completed'
