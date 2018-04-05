import requests
from bs4 import BeautifulSoup
import json

def checkWeather():
	with open('apikey.json')  as fp:
		keys = json.load(fp)
	key = keys['nea']
	url = 'http://api.nea.gov.sg/api/WebAPI/?dataset=2hr_nowcast&keyref=' + key
	s = requests.Session()
	r = s.get(url)
	soup = BeautifulSoup(r.text, "html5lib")
	w = soup.find_all('area')
	weather = []
	for item in w:
	    forecast = item.get('forecast')
	    name = item.get('name')
	    weather.append([forecast, name])
	rain = ['HG', 'HR', 'HS', 'LR', 'LS',
	        'PS', 'RA', 'SH', 'SR', 'WS',
	        'HT', 'TL']
	areas = []
	for onearea in weather:
	    if onearea[0] in rain:
	        areas.append((onearea[1].upper(), 1))
	    else:
	    	areas.append((onearea[1].upper(), 0))
	return areas

print('Start process')
print(checkWeather())
print ("process completed")
