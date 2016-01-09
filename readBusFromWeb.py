from lxml import html
import lxml.html
import urllib2
import requests
import urllib
import unidecode
import os
import time

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

def parseBusRow(rows):
	print rows
	for i in range(0,len(rows)-1,4):
		distance = rows[i]
		busstopnumber = unidecode.unidecode(rows[i+2])
		busstop = unidecode.unidecode(rows[i+3])
		print distance+' '+busstopnumber+' '+busstop

def parseBusFile(busnumber):
	datafolder = '~/Dropbox/project/busstoppy/busFromWeb/'
	filename =datafolder + busnumber +'.html'
	with open(os.path.expanduser(filename),'r') as f:
		a = f.read()
	# print a
	doc = html.fromstring(a)
	# rows = doc.xpath('//table[@border="0" and @cellpadding="0"]/tr/td[position()=1]/form/section/table/td/text()')
	# parseBusRow(rows)
	rows = doc.xpath('//table[@border="0" and @cellpadding="0"]/tr/td[position()=3]/form/section/table/tr/td/text()')
	parseBusRow(rows)

parseBusFile('2')