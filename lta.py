import json
from urlparse import urlparse
import httplib2 as http
__author__ = 'Jiang'
# Class to extract busstop/bus json data from LTA API
# There are 7 types of data:
# 1. busstop
# 2. sbsbusroute
# 3. sbsbusservice
# 4. smrtbusroute
# 5. smrtbusservice
# 6. arrivaltime
# 7. taxi


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
            self.path = '/ltaodataservice.svc/BusStopCodeSet?$skip='
            self.filename = 'busstopdynamic.json'
        elif type == 'sbsbusroute':
            self.path = '/ltaodataservice.svc/SBSTRouteSet?$skip='
            self.filename = 'sbsbusroute.json'
        elif type == 'sbsbusservice':
            self.path = '/ltaodataservice.svc/SBSTInfoSet?$skip='
            self.filename = 'sbsbusservice.json'
        elif type == 'smrtbusroute':
            self.path = '/ltaodataservice.svc/SMRTRouteSet?$skip='
            self.filename = 'smrtbusroute.json'
        elif type == 'smrtbusservice':
            self.path = '/ltaodataservice.svc/SMRTInfoSet?$skip='
            self.filename = 'smrtbusservice.json'
        elif type == 'arrivaltime':
            self.path = '/ltaodataservice/BusArrival?BusStopID='
            self.uri = 'http://datamall2.mytransport.sg'
        elif type == 'taxi':
            self.path = '/ltaodataservice/TaxiAvailability?$skip='
            self.uri = 'http://datamall2.mytransport.sg'

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
            i = i+1
            a = len(jsonData['d'])
            print i, a
            for item in jsonData['d']:
                ltadata.append(item)
            if a < 50:
                filename = 'data\\' + self.filename
                json.dump(ltadata, open(filename, 'w'))
                break
