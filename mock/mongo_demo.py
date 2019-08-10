import pymongo
from bson.objectid import ObjectId

client = pymongo.MongoClient('server')
db = client['qingshu']
table = db['book']
print(table.find_one())

find = table.find_one({'_id': ObjectId('5d3d9a35d91cb342c9edf32d')})

# table.update({'_id': "ObjectId('5d3d67dd7d38eb1b04db9838')"}, {})

print(find)

print(table.update({'_id': ObjectId("5d3d9a35d91cb342c9edf32d")}, {'$set': {'name': 'dad'}}))