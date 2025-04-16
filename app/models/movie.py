from datetime import datetime

from bson import ObjectId


class Movie:
    @staticmethod
    def create(mongo, data):
        """Insert a new movie"""
        data['created_at'] = datetime.utcnow()
        return mongo.db.movies.insert_one(data)

    @staticmethod
    def get_all(mongo):
        """Get all movies"""
        return list(mongo.db.movies.find().limit(50))

    @staticmethod
    def get_by_id(mongo, movie_id):
        """Get single movie by ID"""
        return mongo.db.movies.find_one({"_id": movie_id})

    @staticmethod
    def get_latest(mongo):
        "les derniers films sortis"
        return mongo.db.movies.find().sort("created_at", -1).limit(10)

    @staticmethod
    def get_popular(mongo):
        "films les plus pop"
        return mongo.db.movies.find().sort("popularity", -1).limit(10)

    @staticmethod
    def get_all_cursor(mongo, last_id=None, per_page=10):
        """Get all movies with pagination"""
        query = {}
        if last_id:
            query = {"_id": {"$gt": ObjectId(last_id)}}
        return (mongo.db.movies
                .find(query)
                .sort("_id", 1)
                .limit(per_page))
