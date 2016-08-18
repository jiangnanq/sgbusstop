from lta import *
from processdata import *
__author__ = 'Jiang Nanqing'

# Step 1: Read dynamic data from LTA datamall
# This step will generate 5 json files in data directory
# busstop = lta('smrtbusservice')
# busstop = lta('sbsbusservice')
# busstop = lta('smrtbusroute')
# busstop = lta('sbsbusroute')
# busstop = lta('busstop')
# busstop = lta('busServices')
# busstop = lta('busRoutes')
# busstop.readDataFromLTA()

# Step 2: process data with relative function

# Generate busline for each busline
# This step will generate busline.json
# note: this step is replaced by a python program
# 		to read bus line information from transitlink.com.sg
#		The bus information provided by LTA is outdated
# test = processdata().processbusroutes()

# Process MRT information
# Update mrt.json file
# test = processdata().processmrt()

# Process shopping mall information
# Update mall.json file
# test = processdata().processmalldata()

# Process special bus 243/410/225
# This function must implement once after 
# update the busline from transitlink.com.sg
# test = processdata().processSpecialBus()

# Generate busstop.json with MRT&Mall information
# test = processdata().combinebusstopinfo()

# Generate busstop file for translate
# test = processdata().exportAllBusStops()

test = processdata()
test.exportBusStop()
# test.processbusroutes()
print 'process completed'
