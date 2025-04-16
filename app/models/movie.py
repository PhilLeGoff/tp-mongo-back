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
    def get_latest(mongo, limit=10):
        """les derniers films sortis"""
        return list(mongo.db.movies.find(
                {"release_date": {"$exists": True, "$ne": ""}},
                {"_id": 0}
            ).sort("release_date", -1).limit(limit))

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

    @staticmethod
    def get_title_frequency(mongo):
                """Get the most repeated word count in movie titles"""
                from collections import Counter

                titles = mongo.db.movies.distinct("title")  # Get all unique titles
                words = []
                excluded_words = {"the", "a", "an", "of", "-", "_", "and", "in", "to", "de", "&"}  # Set of articles to exclude
                for title in titles:
                    words.extend(word for word in title.split() if word.lower() not in excluded_words)

                word_counts = Counter(words)  # Count word frequencies
                return word_counts.most_common(1)  # Return the most common word and its count

    @staticmethod
    def get_popular_movies(mongo, limit=10):
        return list(
            mongo.db.movies.find({}, {"_id": 0})
            .sort("popularity", -1)
            .limit(limit)
        )
