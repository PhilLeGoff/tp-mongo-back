from datetime import datetime


class Movie:
    @staticmethod
    def create(mongo, data):
        """Insert a new film"""
        data['created_at'] = datetime.utcnow()
        return mongo.db.movies.insert_one(data)

    @staticmethod
    def get_all(mongo):
        """Get all posts"""
        return list(mongo.db.movies.find().limit(50))

    @staticmethod
    def get_by_id(mongo, movie_id):
        """Get single post by ID"""
        return mongo.db.movies.find_one({"_id": movie_id})
