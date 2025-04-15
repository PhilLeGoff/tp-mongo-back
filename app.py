import configparser
import os
from collections import Counter

from flask import Flask, jsonify, request
from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
from flask_pymongo import PyMongo
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config["MONGO_URI"] = os.getenv("DB_URI")
mongo = PyMongo(app, tlsCAFile=certifi.where())

@app.route('/')
def home():  # put application's code here
    return 'Hello World!'

@app.route("/get", methods=["GET"])
def get_data():
    data = list(mongo.db.movies.find({}, {"_id": 0}).limit(50))
    return jsonify(data), 200

@app.route("/genres/popular", methods=["GET"])
def get_common_genres():
    all_movies = mongo.db.movies.find({}, {"genres": 1})
    
    genres = []
    for movie in all_movies:
        if "genres" in movie and isinstance(movie["genres"], list):
            for g in movie["genres"]:
                if isinstance(g, dict) and "name" in g:
                    genres.append(g["name"])
                elif isinstance(g, str):
                    genres.append(g)
    
    genre_counts = Counter(genres)
    sorted_genres = genre_counts.most_common()

    return jsonify(sorted_genres), 200

@app.route("/genres/<genre_name>", methods=["GET"])
def get_movies_by_genre(genre_name):
    query = {
        "genres": {
            "$elemMatch": {
                "name": {"$regex": f"^{genre_name}$", "$options": "i"}
            }
        }
    }
    movies = list(mongo.db.movies.find(query, {"_id": 0}))
    return jsonify(movies), 200

if __name__ == '__main__':
    app.run()
