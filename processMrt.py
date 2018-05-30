import os
import xlrd
import json

print ('start process')
fname = '~/Dropbox/project/busstoppy/inputdata/MRT.xlsx'
xl_workbook = xlrd.open_workbook(os.path.expanduser(fname))
xl_sheet = xl_workbook.sheet_by_index(0)
num_cols = xl_sheet.ncols
mrt = {}
for row_idx in range(1, xl_sheet.nrows):
    onerow = xl_sheet.row(row_idx)
    key = onerow[0].value
    name = onerow[1].value
    namec = onerow[2].value
    lat = float(onerow[3].value)
    long = float(onerow[4].value)
    mapChnX = int(onerow[8].value)
    mapChnY = int(onerow[9].value)
    mapStatusX = int(onerow[10].value)
    mapStatusY = int(onerow[11].value)
    mrt[key] = [name, namec, lat, long, mapChnX, mapChnY, mapStatusX, mapStatusY]

# with open('mrt.json', 'w') as fp:
#    json.dump(mrt, fp)
# fp.close()
print ('process complete')
