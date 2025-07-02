from fastapi import FastAPI
from pymongo import MongoClient

app = FastAPI()

client = MongoClient('mongodb://db:27017/')
db = client['Game']  #db
collection = db['Scores']  #table   

@app.get("/scores")
def read_scores():

    score_dict = {}
    
    for score in collection.find(): 

        score_dict[score['container_name']] = score['score']
    
    return score_dict
