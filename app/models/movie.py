from datetime import datetime, timedelta

from bson import ObjectId
from pymongo import ASCENDING


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
        """films les plus pop"""
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

    @staticmethod
    def get_top_rated_movies(mongo, limit):
        return list(
            mongo.db.movies.find(
                {
                    "poster_path": {"$ne": None}  # or "$exists": True if needed
                },
                {
                    "_id": 0,
                    "title": 1,
                    "vote_average": 1,
                    "poster_path": 1
                }
            ).sort("vote_average", -1).limit(limit)
        )

    @staticmethod
    def get_most_appreciated_genres(mongo, limit):
        pipeline = [
            {"$unwind": "$genres"},
            {"$group": {
                "_id": "$genres.name",
                "avgRating": {"$avg": "$vote_average"},
                "count": {"$sum": 1}
            }},
            {"$sort": {"avgRating": -1, "count": -1}},
            {"$limit": limit}
        ]
        return list(mongo.db.movies.aggregate(pipeline))

    @staticmethod
    def get_available_decades(mongo):
        result = mongo.db.movies.aggregate([
            {
                "$match": {
                    "release_date": {"$exists": True, "$ne": "", "$regex": "^\d{4}-\d{2}-\d{2}$"}
                }
            },
            {
                "$project": {
                    "decade": {
                        "$concat": [
                            {"$toString": {
                                "$multiply": [
                                    {"$floor": {"$divide": [{"$year": {"$toDate": "$release_date"}}, 10]}},
                                    10
                                ]
                            }},
                            "s"
                        ]
                    }
                }
            },
            {"$group": {"_id": "$decade"}},
            {"$sort": {"_id": 1}}
        ])
        return [doc["_id"] for doc in result]

    @staticmethod
    def get_best_movie_for_decade(mongo, decade):
        decade_start = int(decade[:-1])  # "1990s" → 1990
        decade_end = decade_start + 9

        return mongo.db.movies.find_one(
            {
                "release_date": {"$regex": f"^{decade_start}|^{decade_start + 1}|^{decade_end}"},
                "vote_average": {"$gt": 0},
                "vote_count": {"$gt": 0},
                "poster_path": {"$ne": None, "$ne": ""}
            },
            sort=[("vote_average", -1), ("vote_count", -1)],
            projection={"_id": 0, "title": 1, "vote_average": 1, "poster_path": 1}
        )

    @staticmethod
    def get_top_rated_movies(mongo, limit):
        return list(
            mongo.db.movies.find(
                {"vote_count": {"$gte": 500}, "poster_path": {"$ne": None}},
                {"_id": 0, "title": 1, "vote_average": 1, "vote_count": 1, "poster_path": 1}
            ).sort([("vote_average", -1), ("vote_count", -1)]).limit(limit)
        )

    @staticmethod
    def get_underrated_gems(mongo, limit):
        return list(
            mongo.db.movies.find(
                {"vote_average": {"$gte": 7}, "vote_count": {"$lte": 100}, "poster_path": {"$ne": None}},
                {"_id": 0, "title": 1, "vote_average": 1, "vote_count": 1, "poster_path": 1}
            ).sort("vote_average", -1).limit(limit)
        )

    @staticmethod
    def get_hottest_movies(mongo, limit):
        three_months_ago = datetime.now() - timedelta(days=90)

        return list(
            mongo.db.movies.find(
                {
                    "release_date": {"$gte": three_months_ago.strftime("%Y-%m-%d")},
                    "vote_count": {"$gte": 100},
                    "vote_average": {"$gte": 6.0},
                    "poster_path": {"$ne": None}
                },
                {
                    "_id": 0,
                    "title": 1,
                    "vote_average": 1,
                    "vote_count": 1,
                    "release_date": 1,
                    "poster_path": 1
                }
            ).sort([("vote_average", -1), ("vote_count", -1)]).limit(limit)
        )
    @staticmethod
    def get_new_releases(mongo):
        return list(mongo.db.movies.find(
            {"release_date": {"$exists": True, "$ne": ""}},
            {"_id": 0, "title": 1, "poster_path": 1, "release_date": 1}
        ).sort("release_date", -1).limit(15))

    @staticmethod
    def get_most_popular(mongo):
        return list(mongo.db.movies.find(
            {"poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1, "popularity": 1}
        ).sort("popularity", -1).limit(15))

    @staticmethod
    def get_critically_acclaimed(mongo):
        return list(self.mongo.db.movies.find(
            {"vote_average": {"$gte": 8}, "vote_count": {"$gt": 1000}},
            {"_id": 0, "title": 1, "poster_path": 1, "vote_average": 1}
        ).sort("vote_average", -1).limit(15))

    @staticmethod
    def get_long_movies(mongo):
        return list(mongo.db.movies.find(
            {"runtime": {"$gte": 150}, "poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1, "runtime": 1}
        ).limit(15))

    @staticmethod
    def get_short_movies(mongo):
        return list(mongo.db.movies.find(
            {"runtime": {"$lte": 90}, "poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1, "runtime": 1}
        ).limit(15))

    @staticmethod
    def get_movies_by_decade(mongo, start_year):
        return list(mongo.db.movies.find(
            {"release_date": {"$regex": f"^{start_year}"}},
            {"_id": 0, "title": 1, "poster_path": 1}
        ).limit(15))

    @staticmethod
    def get_movies_by_genre(mongo, genre_name):
        return list(mongo.db.movies.find(
            {"genres.name": genre_name, "poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1}
        ).limit(15))

    @staticmethod
    def get_true_stories(mongo):
        return list(mongo.db.movies.find(
            {"overview": {"$regex": "true story", "$options": "i"}},
            {"_id": 0, "title": 1, "poster_path": 1}
        ).limit(15))

    @staticmethod
    def search_movies(mongo, keyword, genre):
        pipeline = []

        if keyword:
            pipeline.append({
                "$match": {
                    "title": {
                        "$regex": keyword,
                        "$options": "i"  # insensitive
                    }
                }
            })

        if genre:
            pipeline.append({
                "$match": {
                    "genres.name": genre  # match si "genres": ["Action", "Sci-Fi"]
                }
            })
        # Optional: sort by title
        # pipeline.append({"$sort": {"title": ASCENDING}})
        pipeline.append({"$limit": 10})
        print(pipeline)
        movies = list(mongo.db.movies.aggregate(pipeline))
        # print(movies)
        return movies
