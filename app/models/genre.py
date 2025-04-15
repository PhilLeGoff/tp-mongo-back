from datetime import datetime


class Genre:
    @staticmethod
    def create(mongo, data):
        """Insert a new genre"""
        data['created_at'] = datetime.utcnow()
        return mongo.db.genres.insert_one(data)

    @staticmethod
    def get_all(mongo):
        """Get all posts"""
        return list(mongo.db.genres.find().limit(50))

    @staticmethod
    def get_by_id(mongo, genre_id):
        """Get single post by ID"""
        return mongo.db.genres.find_one({"_id": genre_id})
