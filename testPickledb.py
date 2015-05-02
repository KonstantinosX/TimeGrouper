import pickledb

db = pickledb.load('test.db',False)
db.set('testJSON',{'name':'hi_1', 'timeseries': '1,2,3,4,543,2,4354,54', 'updateMech': 'SU'})

print db.get('testJSON')['name']
