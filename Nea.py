import requests
import json
from bs4 import BeautifulSoup
print 'Start process'
key = '781CF461BB6606ADEA6B1B4F3228DE9D5024E401E592608F'
url = 'http://api.nea.gov.sg/api/WebAPI/?dataset=2hr_nowcast&keyref=' + key
print url
s = requests.Session()
r = s.get(url)
soup = BeautifulSoup(r.text, 'xml')
w = soup.find_all('area')
weather = []
for item in w:
    forecast = item.get('forecast')
    name = item.get('name')
    weather.append([forecast, name])
# rain = ['HG','HR','HS','LR','LS','PS','RA','SH','SR','WS']
print ("process completed")