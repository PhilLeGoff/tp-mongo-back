import configparser
import os

from flask import Flask, jsonify, request
from pymongo import MongoClient
import certifi
from flask_pymongo import PyMongo

app = Flask(__name__)

config = configparser.ConfigParser()
config.read(os.path.abspath(os.path.join(".ini")))

# Configuration MongoDB
app.config["MONGO_URI"] = config['PROD']['DB_URI']
# Initialize PyMongo with SSL certificate validation
mongo = PyMongo(app, tlsCAFile=certifi.where())
@app.route('/')
def home():  # put application's code here
    return 'Hello World!'

@app.route("/get", methods=["GET"])
def get_data():
    data = list(mongo.db.movies.find({}, {"_id": 0}).limit(50))
    return jsonify(data), 200

if __name__ == '__main__':
    app.run()
