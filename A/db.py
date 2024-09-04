
from pymongo import MongoClient

    
CONNECTION_STRING = "mongodb://db:27017/"
client = MongoClient(CONNECTION_STRING)
db = client.get_database('Game')

collection = db.get_collection('Scores') #tablo 


def get_scores(container_nm):
    score = collection.find_one({'container_name':container_nm})
    if score:
        return score['score']
    return 0

def upsert_score(container_nm,score):
    collection.update_one({'container_name':container_nm}, {'$set': {'score': score}}, upsert=True)