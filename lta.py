import json
from urllib.parse import urlparse
import httplib2 as http
import requests
import zipfile
import io

__author__ = 'Nanqing'
# All information should been extract


class Lta:
    path = ''
    headers = {}
    uri = 'http://datamall2.mytransport.sg/ltaodataservice/'
    ltatype = {'busstop': 'BusStops?$skip=',
               'busRoute': 'BusRoutes?$skip=',
               'taxi': 'Taxi-Availability?$skip='}
    headers = {
        'AccountKey': "QbJYYDbzk2V605i6JBXPHA==",
        'UniqueUserID': "5aa27f9b-74fd-4bb6-8f4e-3a9aa47613bb",
        'accept': 'application/json'}
    url = 'http://datamall2.mytransport.sg/' + \
        'ltaodataservice/'

    def __init__(self):
        # init class base on the appoint class type
        with open('apikey.json') as fp:
            keys = json.load(fp)
        self.AccountKey = keys['lta_accountkey']
        self.UniqueUserID = keys['lta_userid']
        self.headers = {
            'AccountKey': self.AccountKey,
            'UniqueUserID': self.UniqueUserID,
            'accept': 'application/json'}

    def GetDataFromLta(self, i, path):
        # send request to LTA and return reply json data
        target = urlparse(self.uri + path + i)
        print (target.geturl())
        method = 'GET'
        body = ''
        h = http.Http()
        response, content = h.request(
            target.geturl(),
            method,
            body,
            self.headers)
        jsonObj = json.loads(content)
        return jsonObj

    def readDataFromLTA(self, path):
        # Read LTA data base on the class type
        ltadata = []
        i = 0
        while True:
            step = str(i * 500)
            jsonData = self.GetDataFromLta(step, path)
            i = i+1
            a = len(jsonData['value'])
            for item in jsonData['value']:
                ltadata.append(item)
            if a < 500:
                return ltadata

    def readTaxiFromlta(self):
        taxi = self.readDataFromLTA('Taxi-Availability?$skip=')
        with open('data/ltataxi.json', 'w') as fp:
            json.dump(taxi, fp)
        return taxi

    def readBusRouteFromlta(self):
        busroutedata = self.readDataFromLTA('BusRoutes?$skip=')
        with open('data/ltabusroute.json', 'w') as fp:
            json.dump(busroutedata, fp)

    def readBusStopFromlta(self):
        busstopdata = self.readDataFromLTA('BusStops?$skip=')
        with open('data/ltabusstop.json', 'w') as fp:
            json.dump(busstopdata, fp)
        return busstopdata

    def checkbusarrival(self, busstop):
        h = {'AccountKey': self.AccountKey, 'accept': 'application/json'}
        url = 'http://datamall2.mytransport.sg'
        + '/ltaodataservice/BusArrivalv2?BusStopCode='
        + busstop
        s = requests.Session()
        r = s.get(url, headers=h)
        d = json.loads(r.text)['Services']
#         with open('busschedule.json', 'w') as fp:
#            json.dump(d, fp)
        return d

    def check_volume(self, month_to_check):
        def check(url):
            r = requests.get(u, headers=self.headers).content
            url = json.loads(r.decode('utf-8'))['value'][0]['Link']
            print(url)
            r = requests.get(url)
            if r.ok:
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z.extractall(path='ltadata')
            else:
                print('error to download csv file')
            return r.ok
        url = ['Bus', 'Train', 'ODBus', 'ODTrain']
        for oneurl in url:
            u = self.url + 'PV/' + oneurl + '?Date=' + month_to_check
            print(check(u))

if __name__ == '__main__':
    print("start processing...")
    a = Lta()
#    a.readBusStopFromlta()
#    a.readBusRouteFromlta()
    print('process completed.')
