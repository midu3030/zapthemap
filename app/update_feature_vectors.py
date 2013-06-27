from pymongo import Connection
from bson.code import Code
from pymongo import MongoClient
from bson.binary import Binary
from numpy import *
import cPickle


#'''
#Open a connection to MongoDb (localhost)
#connection =  Connection()
#db = connection.test

def delete_feature_vectors():
    client = MongoClient()
    db = client.mails6
    db.alltextmail.update({"_id" : { "$exists" : True }}, { "$set" : { 'wordfreqs': None }, }, multi=True)    
    

def update_feature_vectors():
    client = MongoClient()
    db = client.mails6
    
    #create an empty array
    wordfreqs = empty([2000]) #array('H',(0,)*2000)
    
    words = {}
    
    #create dictionary storing word vector indices
    i = 0
    for word in db.word_frequencies2.find().limit(2000).sort([("value.count",-1)]):
        words[word['_id']] = i
        i = i + 1
    
    mails = db.alltextmail
     
    for mail in mails.find(timeout=False):
        try:
            for word in mail['body'].split():
                index = words.get(word.lower()) 
                if index is not None:
                    wordfreqs[index] = wordfreqs[index] + 1
        except:
            print "no body?"
            
        bindump = cPickle.dumps( wordfreqs, protocol=2)
        
        db.alltextmail.update({ "_id" : mail['_id'] }, { "$set" : { 'wordfreqs': Binary( bindump ) }, })    
        for i in range(2000):
            wordfreqs[i] = 0


update_feature_vectors()

