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
# note: this step is replaced by a python program
# 		to read bus line information from transitlink.com.sg
#		The bus information provided by LTA is outdated
# test = processdata().processbusroute()

# Process MRT information
# Update mrt.json file
# test = processdata().processmrt()

# Process shopping mall information
# Update mall.json file
# test = processdata().processmalldata()

# Generate busstop.json with MRT&Mall information
# test = processdata().combinebusstopinfo()

# Process special bus 225W/225G, 243W/243G, 410W/410G
# The First/Last stop need to manully update
# test = processdata().processSpecialBus()

print 'process completed'