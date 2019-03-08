import csv
import json


class Hot_busstop:
    def __init__(self):
        self.volume = self.readVolume()

    def readVolume(self):
        volume = {}
        with open('ltadata/transport_node_bus_201809.csv') as fp:
            reader = csv.reader(fp)
            for onerow in reader:
                busstop_number = onerow[4]
                tap_out = onerow[6]
                hour = onerow[2]
                day_type = onerow[1]
                if busstop_number in volume.keys():
                    volume[busstop_number].append((day_type, hour, tap_out))
                else:
                    volume[busstop_number] = [(day_type, hour, tap_out)]
        del volume['PT_CODE']
        return volume

    def sort_busstop(self, is_weekday, time_hour):
        w = 'WEEKDAY' if is_weekday else 'WEEKENDS/HOLIDAY'
        busstops = []
        for k, v in self.volume.items():
            try:
                tap_out = list(filter(lambda x: x[0] == w
                                      and x[1] == time_hour,
                                      v))[0][2]
            except:
                continue
            busstops.append((k, int(tap_out)))
        busstops.sort(key=lambda x: x[1], reverse=True)
        return busstops[0:100]

    def get_mrt_busstop(self):
        with open('data/mrt.json') as fp:
            mrt = json.load(fp)
        mrtbusstops = []
        for k, v in mrt.items():
            mrtnumber = ''.join([i for i in k if not i.isdigit()])
            if mrtnumber in ['EW', 'CC', 'NS', 'DT', 'NE']:
                mrtbusstops += v[1]
        mrtbusstops = list(set(mrtbusstops))
        return mrtbusstops

    def get_busstop(self):
        with open('data/busstop.json') as fp:
            busstops = json.load(fp)
        return busstops

    def get_hot_busstop(self):
        weekday = {}
        weekend = {}
        hot_stop = []
        for i in range(0, 24):
            k = 'weekday_{0:0=2d}'.format(i)
            print(k)
            weekday[str(i)] = self.sort_busstop(True, str(i))
            weekend[str(i)] = self.sort_busstop(False, str(i))
        for k, v in weekday.items():
            for onestop in v:
                hot_stop.append(onestop[0])
        for k, v in weekend.items():
            for onestop in v:
                hot_stop.append(onestop[0])
        h = list(set(hot_stop) - set(self.get_mrt_busstop()))
        b = self.get_busstop()
        result = {}
        for onestop in h:
            if onestop in b:
                result[onestop] = b[onestop][0]
        return weekday, weekend, result


if __name__ == '__main__':
    print('Start to process...')
    h = Hot_busstop()
    wd, wk, bustop = h.get_hot_busstop()
#    with open('data/hotbusstop.json', 'w') as fp:
#        json.dump(h.get_hot_busstop(), fp)
    print('process completed.')
