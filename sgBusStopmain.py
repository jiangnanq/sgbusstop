from processdata import Lta, Local
from datetime import datetime
__author__ = 'Jiang Nanqing'

print 'start processing - {:%H:%M:%S}'.format(datetime.now())

# Step 1: Read data from LTA
# busStop('lta')
# a = lta()
# a.readBusStopFromlta()
# a.readBusRouteFromlta()

# Step 2: process busroute and busstop data from LTA
a = Local()
a.processBusStops()
# a.processBusLines()
# a.saveBusstopTofile()

print 'process completed - {:%H:%M:%S}'.format(datetime.now())
