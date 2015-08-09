__author__ = 'Jiang'
#Class to extract busstop/bus json data from LTA API
import json
import time
import urllib
from urlparse import urlparse
import httplib2 as http
class lta:
    AccountKey='QbJYYDbzk2V605i6JBXPHA=='
    UniqueUserID='5aa27f9b-74fd-4bb6-8f4e-3a9aa47613bb'
    uri='http://datamall.mytransport.sg'
    path=''
    headers={}
    type=''
    def __init__(self,type):
        self.type=type
        self.headers={'AccountKey':'QbJYYDbzk2V605i6JBXPHA==',
             'UniqueUserID':'5aa27f9b-74fd-4bb6-8f4e-3a9aa47613bb',
             'accept':'application/json'}
        if type=='busstop':
            self.path='/ltaodataservice.svc/BusStopCodeSet?$skip='
        elif type=='sbsbusroute':
            self.path='/ltaodataservice.svc/SBSTRouteSet?$skip='
        elif type=='sbsbusservice':
            self.path='/ltaodataservice.svc/SBSTInfoSet?$skip='
        elif type=='smrtbusroute':
            self.path='/ltaodataservice.svc/SMRTRouteSet?$skip='
        elif type=='smrtbusservice':
            self.path='/ltaodataservice.svc/SMRTInfoSet?$skip='
        elif type=='arrivaltime':
            self.path='/ltaodataservice/BusArrival?BusStopID='
            self.uri='http://datamall2.mytransport.sg'
        elif type=='taxi':
            self.path='/ltaodataservice/TaxiAvailability?$skip='
            self.uri='http://datamall2.mytransport.sg'
    def GetDataFromLta (self,i):
        self.path+=i
        target=urlparse(self.uri+self.path);
        print target.geturl()
        method='GET'
        body=''
        h=http.Http()
        response, content=h.request(
            target.geturl(),
            method,
            body,
            self.headers)
        jsonObj=json.loads(content)
        return jsonObj
