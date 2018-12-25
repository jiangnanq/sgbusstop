from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
import json


class Area:
    allarea = {}

    def __init__(self):
        # read plan area poly shape data
        with open('inputdata/planarea.json') as fp:
            area = json.load(fp)
        for oneAread in area:
            areaname = oneAread['pln_area_n']
            areapoly = Polygon(json.loads(oneAread['geojson'])
                               ['coordinates'][0][0])
            self.allarea[areaname] = areapoly

    def checkArea(self, latitude, longitude):
        areaname = ''
        point = Point(longitude, latitude)
        for aname, apoly in self.allarea.items():
            if apoly.contains(point):
                areaname = aname
                break
        return areaname

if __name__ == '__main__':
    print('start process')
    a = Area()
    print('process completed.')
