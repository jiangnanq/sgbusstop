from lxml import html
import lxml.html
import urllib2
import requests
import urllib
import unidecode
import os
import time
import json

def readBusLines():
	datafolder = '~/Dropbox/project/busstoppy/busFromWeb/'
	filename = datafolder + 'busFromWeb.txt'
	with open(os.path.expanduser(filename)) as f:
		buses = f.read().splitlines()
	return buses

def readBusLineFromWeb(buses):
	url = "http://www.transitlink.com.sg/eservice/eguide/service_route.php?service="

	for abus in buses:
		datafolder = '~/Dropbox/project/busstoppy/busFromWeb/'
		time.sleep(0.5)
		urlbus = url + abus
		print urlbus
		response = urllib2.urlopen(urlbus)
		webcontent = response.read()
		filename =datafolder + abus +'.html'
		print filename
		with open(os.path.expanduser(filename), 'w') as f:
			f.write(webcontent)

def checkBusStopNumber(rows,startIndex):
	busStopNumber = 0
	for i in range(1,3):
		row = rows[startIndex+i]
		if not isinstance(row,str):
			try:
				int(unidecode.unidecode(row))
				busStopNumber = str(unidecode.unidecode(row)).zfill(5)
			except ValueError:
				continue
		else:
			try:
				busStopNumber = str(int(row)).zfill(5)
			except ValueError:
				continue
	return busStopNumber

def checkFloat(rows,direction):
	a = []
	b = []
	for row in rows:
		if isinstance(row,str):
			try:
				if float(row)<199:
					a.append(float(row))
					startIndex = rows.index(row)
					busstopnumber = checkBusStopNumber(rows,startIndex)
					b.append(str(busstopnumber).strip())
			except ValueError:
				continue
	c = []
	for i in range(0,len(a)):
		abusstop = str(b[i])+':'+str(a[i])
		if direction == 1:
			abusstop = abusstop + ':' + '1'
		else:
			abusstop = abusstop + ':' + '2'
		abusstop = abusstop + ':' + str(i+1)
		c.append(abusstop)
	return c

# def combineBusLine(d1,d2):
# 	reture d1 + d2

def parseBusFile(busnumber):
	datafolder = '~/Dropbox/project/busstoppy/busFromWeb/'
	filename =datafolder + busnumber +'.html'
	with open(os.path.expanduser(filename),'r') as f:
		a = f.read()
	doc = html.fromstring(a)
	rows = doc.xpath('//table[@border="0" and @cellpadding="0"]/tr/td[position()=1]/form/section/table/td/text()')
	direction1 = checkFloat(rows,1)
	rows = doc.xpath('//table[@border="0" and @cellpadding="0"]/tr/td[position()=3]/form/section/table/tr/td/text()')
	direction2 = checkFloat(rows,2)
	alldirections = direction1 + direction2
	return ",".join(alldirections)

# parseBusFile('184')
buslines = {}
for abus in readBusLines():
	buslines[abus] = parseBusFile(abus)
datafolder = '~/Dropbox/project/busstoppy/busFromWeb/'
filename = datafolder + 'buslines.json'
with open(os.path.expanduser(filename),'w') as f:
	json.dump(buslines,f)
print 'process completed!'
