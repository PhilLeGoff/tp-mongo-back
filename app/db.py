from .extensions import mongo

def get_movies_collection():
    return mongo.db.movies

def get_genres_collection():
    return mongo.db.genres