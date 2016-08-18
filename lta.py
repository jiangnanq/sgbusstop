import os
import json
from urlparse import urlparse
import httplib2 as http
__author__ = 'Jiang'
# Class to extract busstop/bus json data from LTA API
# Refer manual of LTA for details


class lta:
    path = ''
    headers = {}
    type = ''

    def __init__(self, type):
        # init class base on the appoint class type
        self.AccountKey = 'QbJYYDbzk2V605i6JBXPHA=='
        self.UniqueUserID = '5aa27f9b-74fd-4bb6-8f4e-3a9aa47613bb'
        self.uri = 'http://datamall.mytransport.sg'
        self.type = type
        self.headers = {
            'AccountKey': 'QbJYYDbzk2V605i6JBXPHA==',
            'UniqueUserID': '5aa27f9b-74fd-4bb6-8f4e-3a9aa47613bb',
            'accept': 'application/json'}
        if type == 'busstop':
            self.path = '/ltaodataservice/BusStops?$skip='
            self.uri = 'http://datamall2.mytransport.sg'
            self.filename = 'busstop.json'
        elif type == 'arrivaltime':
            self.path = '/ltaodataservice/BusArrival?BusStopID='
            self.uri = 'http://datamall2.mytransport.sg'
        elif type == 'taxi':
            self.path = '/ltaodataservice/TaxiAvailability?$skip='
            self.uri = 'http://datamall2.mytransport.sg'
        elif type == 'busServices':
            self.path = '/ltaodataservice/BusServices?$skip='
            self.uri = 'http://datamall2.mytransport.sg'
            self.filename = 'busservices.json'
        elif type == 'busRoutes':
            self.path = '/ltaodataservice/BusRoutes?$skip='
            self.uri = 'http://datamall2.mytransport.sg'
            self.filename = 'busroutes.json'
    def GetDataFromLta(self, i):
        # send request to LTA and return reply json data
        apath = self.path+i
        target = urlparse(self.uri+apath)
        print target.geturl()
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

    def readDataFromLTA(self):
        # Read LTA data base on the class type
        ltadata = []
        i = 0
        while True:
            step = str(i*50)
            jsonData = self.GetDataFromLta(step)
            # print(jsonData)
            i = i+1
            # a = len(jsonData['d'])
            a = len(jsonData['value'])
            print i, a
            for item in jsonData['value']:
                ltadata.append(item)
            if a < 50:
                filename = '~/Dropbox/project/busstoppy/data/' + self.filename
                json.dump(ltadata, open(os.path.expanduser(filename), 'w'))
                break
