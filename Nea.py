import urllib2
import xmltodict
import os
from datetime import datetime
key = '781CF461BB6606ADEA6B1B4F3228DE9D5024E401E592608F'
url = 'http://api.nea.gov.sg/api/WebAPI?dataset=2hr_nowcast&keyref=' + key
print url
rain = ['HG','HR','HS','LR','LS','PS','RA','SH','SR','WS']
response = urllib2.urlopen(url)
webcontent = response.read()
print webcontent
dom = xmltodict.parse(webcontent)
print dom['channel']['item']['weatherForecast']['area'][1]
filename = '~/Dropbox/project/busstoppy/data/weather.txt'
with open(os.path.expanduser(filename), 'w') as f:
    f.write('timestamp:{:%H:%M:%S}'.format(datetime.now()))
    f.write('\n')
    for item in dom['channel']['item']['weatherForecast']['area']:
        f.write(item['@name'] + ', ' + item['@forecast'] + '\n')
f.close()
print ("process completed")