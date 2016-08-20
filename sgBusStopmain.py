from lta import *
from processdata import *
from datetime import datetime
__author__ = 'Jiang Nanqing'

print 'start processing - {:%H:%M:%S}'.format(datetime.now())

# Step 1: Read dynamic data from LTA datamall
# This step will generate 3 json files in data directory
# busstop = lta('busstop')
# busstop = lta('busServices')
# busstop = lta('busRoutes')
# busstop.readDataFromLTA()

# busRoute().processBusRoutes()
# processData().processBusStop()
processData().processBusStop()
# Step 2: process bus routes, generate busline.json
# test = processdata().processbusroutes()

# process bus stop information, fill up with busnumber/MRT/MALL information
# generate busstopsforapps.json
# test.processBusStop()

# Process MRT information
# Update mrtforapps.json file
# test.processmrt()

# Process shopping mall information
# Update mallforapps.json file
# test.processmalldata()

print 'process completed - {:%H:%M:%S}'.format(datetime.now())
