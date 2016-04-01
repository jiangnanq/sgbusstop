import urllib2
import xmltodict
key = '781CF461BB6606ADEA6B1B4F3228DE9D5024E401E592608F'
url = 'http://www.nea.gov.sg/api/WebAPI?dataset=2hr_nowcast&keyref=' + key
print url
response = urllib2.urlopen(url)
webcontent = response.read()
print webcontent
dom = xmltodict.parse(webcontent)
# print dom['channel']['item']['weatherForecast']['area'][1]
for item in dom['channel']['item']['weatherForecast']['area']:
	print item['@name'],item['@forecast']
