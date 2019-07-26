import json
from bs4 import BeautifulSoup
from geopy.distance import geodesic


def busstops():
    with open('../busstop.json') as fp:
        b = json.load(fp)
    allstops = []
    for key, value in b.items():
        allstops.append((key, value[0], value[2], value[3]))
    return allstops


def markets():
    with open('hawker-centres-geojson.geojson') as fp:
        w = json.load(fp)
    markets = []
    for onemarket in w['features']:
        soup = BeautifulSoup(onemarket['properties']['Description'],
                             features='html.parser').find_all('td')
        name = soup[17].get_text()
        stalls = soup[6].get_text()
        lat = onemarket['geometry']['coordinates'][1]
        longitude = onemarket['geometry']['coordinates'][0]
        markets.append((name, lat, longitude, stalls))
    return markets


def getSupermarkets():
    with open('./supermarkets-geojson.geojson') as fp:
        s = json.load(fp)
    supermarket = []
    for onemarket in s['features']:
        soup = BeautifulSoup(onemarket['properties']['Description'],
                             features='html.parser').find_all('td')
        name = soup[0].get_text()
        postcode = soup[4].get_text()
        lat = onemarket['geometry']['coordinates'][1]
        longitude = onemarket['geometry']['coordinates'][0]
        supermarket.append((name, lat, longitude, postcode))
    return supermarket


def sortkey(onerecord):
    return onerecord[-1]


def findNearbyStops(market, allstops):
    allrecords = []
    for onestop in allstops:
        p1 = (float(market[1]), float(market[2]))
        p2 = (float(onestop[2]), float(onestop[3]))
        dis = geodesic(p1, p2).m
        allrecords.append(market + onestop + (dis,))
    return sorted(allrecords, key=sortkey)[0]


if __name__ == '__main__':
    print('Start to process...')
    supermarkets = getSupermarkets()
#    supermarkets = markets()
    stops = busstops()
    allmarkets = []
    for i, onemarket in enumerate(supermarkets):
        if i % 10 == 0:
            print(i)
        allmarkets.append((i,) + findNearbyStops(onemarket, stops))
#    with open('./market.json', 'w') as fp:
#        json.dump(allmarkets, fp)
    print('Process completed.')
