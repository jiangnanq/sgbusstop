from lta import *
from processdata import *
__author__ = 'Jiang'

# Step 1: Read dynamic data from LTA datamall
# This step will generate 5 json files in data directory
# busstop = lta('smrtbusservice')
# busstop = lta('sbsbusservice')
# busstop = lta('smrtbusroute')
# busstop = lta('sbsbusroute')
# busstop = lta('busstop')
# busstop.readDataFromLTA()

# Step 2: process data with relative function

# Generate busline for each busline
# This step will generate busline.json
# test = processdata().processbusroute()

# Generate busstop.json with MRT&Mall information
# test = processdata().combinebusstopinfo()

# Process MRT information
# Update mrt.json file
# test = processdata().processmrt()

# Process shopping mall information
# Update mall.json file
test = processdata().processmalldata
print 'process completed'
