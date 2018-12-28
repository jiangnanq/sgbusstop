import requests
import json
from area import Area
from functools import reduce


class Lta_Taxi:
    headers = {
        'AccountKey': "QbJYYDbzk2V605i6JBXPHA==",
        'UniqueUserID': "5aa27f9b-74fd-4bb6-8f4e-3a9aa47613bb",
        'accept': 'application/json'}
    url = 'http://datamall2.mytransport.sg/' + \
        'ltaodataservice/Taxi-Availability?$skip='

    def test(self):
        r = requests.get(self.url+'0', headers=self.headers)
        return r

    def checkTaxi(self):
        taxi = []
        i = 0
        while True:
            u = self.url + str(i * 500)
            print(u)
            r = requests.get(u, headers=self.headers)
            a = json.loads(r.content)['value']
            taxi = taxi + a
            if len(a) < 500:
                break
            i = i + 1
        with open('inputdata/ltataxi.json', 'w') as fp:
            json.dump(taxi, fp)
        return taxi

    def checkAreaTaxi(self):
        with open('inputdata/ltataxi.json') as fp:
            taxies = json.load(fp)
        area = Area()
        a = {}
        for onearea in list(area.allarea.keys()):
            a[onearea] = 0
        for ataxi in taxies:
            taxiarea = area.checkArea(ataxi['Latitude'], ataxi['Longitude'])
            if taxiarea in list(a.keys()):
                a[taxiarea] = a[taxiarea] + 1
        t = [(k, a[k]) for k in sorted(a, key=a.get, reverse=True)]
        s = reduce((lambda x, y: x+y), list(map(lambda x: x[1], t)))
        return list(map(lambda x: (x[0], x[1] / s * 100.0), t)), s

if __name__ == '__main__':
    print('start process')
    t = Lta_Taxi().checkTaxi()
    print('process completed.')
