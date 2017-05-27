from processdata import *
from datetime import datetime
__author__ = 'Jiang Nanqing'

print 'start processing - {:%H:%M:%S}'.format(datetime.now())


# Step 1: Read data from LTA
# busStop('lta')
a=lta()

# Step 2: process bus routes, check bus routes for missing busstop
# a = busRoute('')
# a.processBusRoutes()
# a.checkBuslines()

# Step 3: process busstop, mrt, mall, generate json file in data folder
# processData().processBusStop()
# processData().processmrt()
# processData().processmall()

print 'process completed - {:%H:%M:%S}'.format(datetime.now())
