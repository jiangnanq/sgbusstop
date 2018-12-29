import json
import csv
from geopy.distance import vincenty
from area import Area


class Mrt:
    mrtstations = {}

    def __init__(self):
        stations = []
        a = Area()
        with open('inputdata/mrt.csv') as fp:
            reader = csv.DictReader(fp)
            for row in reader:
                stations.append(row)
        for onestation in stations:
            station_number = onestation['Number']
            name = onestation['Name']
            name_chn = onestation['Name_chn']
            latitude = onestation['Latitude']
            longitude = onestation['Longitude']
            area = a.checkArea(float(latitude), float(longitude))
            self.mrtstations[station_number] = [name,
                                                latitude,
                                                longitude,
                                                name_chn,
                                                area]

    def processMrtStations(self):
        with open("data/busstop.json") as fp:
            busstop = json.load(fp)
        mrtBus = {}
        for mrtnumber, mrtstation in self.mrtstations.items():
            mrtbusstop = {}
            p1 = (mrtstation[1], mrtstation[2])
            for busstopnumber, busstation in busstop.items():
                p2 = (busstation[2], busstation[3])
                mrtbusstop[busstopnumber] = vincenty(p1, p2).m
            sortedmrtbusstop = sorted(mrtbusstop.items(), key=lambda x: x[1])
            top3 = []
            for abusstop in sortedmrtbusstop[0:3]:
                top3.append(abusstop[0])
            mrtBus[mrtnumber] = [mrtstation, top3]
        return mrtBus

if __name__ == '__main__':
    print ('start process')
    m = Mrt().processMrtStations()
    # with open('data/mrt.json', 'w') as fp:
    #    json.dump(mrt, fp)
    # fp.close()
    print ('process complete')
