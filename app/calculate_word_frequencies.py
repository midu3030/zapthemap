from pymongo import Connection
from bson.code import Code

from pymongo import MongoClient

#'''
#Open a connection to MongoDb (localhost)
#connection =  Connection()
#db = connection.test


client = MongoClient()
db = client.mails6 

#Load map and reduce functions
mmap = Code(open('wordMap.js','r').read())
mreduce = Code(open('wordReduce.js','r').read())


#Run the map-reduce query
results = db.alltextmail.map_reduce(mmap, mreduce, "word_frequencies2")

#Print the results
for result in results.find():
    print result['_id'] , result['value']['count']
    