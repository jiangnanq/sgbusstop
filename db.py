import sqlite3
from datetime import datetime
import json


def readHawker():
    with open('./data/hawker.json') as fp:
        hawker = json.load(fp)
    hawker = [(a[1], a[2], a[3], a[5], 0) for a in hawker]
    return hawker


def readSupermarket():
    with open('./data/supermarkets.json') as fp:
        market = json.load(fp)
    return [(m[1],
             m[2],
             m[3],
             m[5],
             1) for m in market]


def saveToDb(sql, records):
    conn = sqlite3.connect('data/busstop.db')
    cur = conn.cursor()
    cur.executemany(sql, records)
    conn.commit()
    conn.close()


def readBusstop():
    with open('data/busstop.json') as fp:
        busstop = json.load(fp)
    stops = []
    for key, value in busstop.items():
        stops.append((key, value[2], value[3], value[0]))
    return stops


def readBusline():
    with open('data/busroute.json') as fp:
        busline = json.load(fp)
    line = []
    for key, value in busline.items():
        for onestop in value:
            line.append((key, onestop[0], onestop[1], float(onestop[2]),
                         int(onestop[3])))
    return line


if __name__ == '__main__':
    print('Start to process {}'.format(datetime.now().strftime('%H:%M:%S')))
    sql = '''INSERT INTO busline(
                               number,
                               busstop,
                               direction,
                               distance,
                               seq) VALUES (?, ?, ?, ?, ?)'''
    line = readBusline()
    print('Process completd {}'.format(datetime.now().strftime('%H:%M:%S')))
