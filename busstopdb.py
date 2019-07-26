import sqlite3
from datetime import datetime
import csv
import json

sqlite_file = 'data/busstop.db'
table1 = 'busstopvolume'
sql_create_table1 = '''CREATE TABLE IF NOT EXISTS busstopvolume (
                       id integer PRIMARY KEY AUTOINCREMENT,
                       busstopnumber TEXT NOT NULL,
                       hour integer NOT NULL,
                       day TEXT NOT NULL,
                       year_month TEXT NOT NULL,
                       tapin integer NOT NULL,
                       tapout intger NOT NULL);'''
sql_create_table2 = '''CREATE TABLE mrt(
                       id integer PRIMARY KEY AUTOINCREMENT,
                       number TEXT NOT NULL,
                       latitude real NOT NULL,
                       longitude real NOT NULL,
                       name TEXT NOT NULL,
                       namechn TEXT NOT NULL,
                       area TEXT NOT NULL,
                       line TEXT NOT NULL,
                       busstopnumber TEXT NOT NULL);'''
sql_create_table3 = '''CREATE TABLE busstop(
                      id integer PRIMARY KEY AUTOINCREMENT,
                      number TEXT NOT NULL,
                      latitude real NOT NULL,
                      longitude real NOT NULL,
                      street TEXT,
                      name TEXT NOT NULL,
                      namechn TEXT,
                      area TEXT NOT NULL,
                      buscount integer NOT NULL,
                      mrtstation TEXT);'''
sql_create_table4 = '''CREATE TABLE busline(
                       id integer PRIMARY KEY AUTOINCREMENT,
                       number TEXT NOT NULL,
                       busstop TEXT NOT NULL,
                       direction TEXT NOT NULL,
                       distance real NOT NULL,
                       seq integer NOT NULL);'''
sql_insert_records1 = '''INSERT INTO busstopvolume( busstopnumber,
                                                   hour,
                                                   day,
                                                   year_month,
                                                   tapin,
                                                   tapout)
                                                    VALUES(?, ?, ?, ?, ?, ?)'''
sql_insert_records2 = '''INSERT INTO mrt(
                        number,
                        latitude,
                        longitude,
                        name,
                        namechn,
                        area,
                        line,
                        busstopnumber)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?)'''
sql_insert_records3 = '''INSERT INTO busstop (number,
                                              latitude,
                                              longitude,
                                              street,
                                              name,
                                              namechn,
                                              area,
                                              buscount,
                                              mrtstation)
                                              VALUES(?, ?, ?, ?, ?, ?, ?, ?,
                                              ?)'''
sql_insert_record4 = '''INSERT INTO busline (number,
                                             busstop,
                                             direction,
                                             distance,
                                             seq)
                                             VALUES(?, ?, ?, ?, ?)'''
sql_query_stop = '''SELECT * FROM busstopvolume WHERE
                    busstopnumber=?
                    AND hour=?'''


class busstopdb:
    def __init__(self):
        self.conn = sqlite3.connect(sqlite_file)
        self.curr = self.conn.cursor()

    def creattalbe(self, sql):
        self.curr.execute(sql)
        self.conn.commit()

    def readdata(self):
        with open('ltadata/transport_node_bus_201809.csv') as fp:
            allrecords = []
            reader = csv.reader(fp)
            for onerow in reader:
                busstop_number = onerow[4]
                day_type = onerow[1]
                hour = onerow[2]
                tap_out = onerow[6]
                tap_in = onerow[5]
                ym = onerow[0]
                allrecords.append([busstop_number,
                                   hour,
                                   day_type,
                                   ym,
                                   tap_in,
                                   tap_out])
            allrecords.pop(0)
            return allrecords

    def readMrt(self):
        with open('data/mrt.json') as fp:
            mrt = json.load(fp)
        mrtinfo = []
        for k, v in mrt.items():
            number = k
            name = v[0][0]
            latitude = v[0][1]
            longtitude = v[0][2]
            chnname = v[0][3]
            area = v[0][4]
            line = ''.join([i for i in k if not i.isdigit()])
            busstop = ''.join([stop + ',' for stop in v[1]])
            mrtinfo.append((number,
                            latitude,
                            longtitude,
                            name,
                            chnname,
                            area,
                            line,
                            busstop))
        return mrtinfo

    def readbusstop(self):
        with open('data/busstop.json') as fp:
            busstop = json.load(fp)
        busstopinfo = []
        for k, v in busstop.items():
            number = k
            latitude = v[2]
            longitude = v[3]
            street = v[4]
            name = v[0]
            namechn = v[1]
            area = v[5]
            buscount = v[6]
            mrtstation = ''.join(m + ',' for m in v[7])
            onestop = (number,
                       latitude,
                       longitude,
                       street,
                       name,
                       namechn,
                       area,
                       buscount,
                       mrtstation)
            busstopinfo.append(onestop)
        return busstopinfo

    def readbusline(self):
        with open('data/busroute.json') as fp:
            busline = json.load(fp)
        buslineinfo = []
        for k, v in busline.items():
            number = k
            for onestop in v:
                busstop = onestop[0]
                direction = onestop[1]
                dis = float(onestop[2])
                seq = int(onestop[3])
                buslineinfo.append((number, busstop, direction, dis, seq))
        return buslineinfo

    def addrecord(self, sql, records):
        self.curr.executemany(sql, records)
        self.conn.commit()

    def querystop(self, stopnumber, hour):
        self.curr.execute(sql_query_stop, (stopnumber, hour))
        a = self.curr.fetchall()
        return a


if __name__ == '__main__':
    print('Start to process {}'.format(datetime.now().strftime('%H:%M:%S')))
    a = busstopdb()
    b = a.readbusline()
    a.addrecord(sql_insert_record4, b)
#    a.creattalbe(sql_create_table4)
#    b = a.querystop('22009', '10')
#    a.addrecord(a.readdata())
    print('Process completd {}'.format(datetime.now().strftime('%H:%M:%S')))
