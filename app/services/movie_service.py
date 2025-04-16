from bson import ObjectId
from datetime import datetime, timedelta

from app.models.movie import Movie


class MovieService:
    def __init__(self, mongo):
        self.mongo = mongo

    def get_movies(self):
        return Movie.get_all(self.mongo)

    def get_movie(self, movie_id):
        return Movie.get_by_id(self.mongo, ObjectId(movie_id))

    def get_popular_movies(mongo, limit=10):
        return list(
            mongo.db.movies.find({}, {"_id": 0})
            .sort("popularity", -1)
            .limit(limit)
        )
    
    def get_latest_movies(self, limit=10):
        return list(
            self.mongo.db.movies.find(
                {"release_date": {"$exists": True, "$ne": ""}},
                {"_id": 0}
            ).sort("release_date", -1).limit(limit)
        )

    def get_top_rated_movies(self, limit=10):
        return list(
            self.mongo.db.movies.find(
                {
                    "poster_path": { "$ne": None }  # or "$exists": True if needed
                },
                {
                    "_id": 0,
                    "title": 1,
                    "vote_average": 1,
                    "poster_path": 1
                }
            ).sort("vote_average", -1).limit(limit)
        )
    def get_most_appreciated_genres(self, limit=5):
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
        return list(self.mongo.db.movies.aggregate(pipeline))
    
    def get_best_movies_by_decade(self):
        decades = self.get_available_decades()
        results = []

        for decade in decades:
            movie = self.get_best_movie_for_decade(decade)
            if movie:
                results.append({
                    "decade": decade,
                    "movie": movie
                })

        return results

    def get_available_decades(self):
        result = self.mongo.db.movies.aggregate([
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

    def get_best_movie_for_decade(self, decade):
        decade_start = int(decade[:-1])  # "1990s" → 1990
        decade_end = decade_start + 9

        return self.mongo.db.movies.find_one(
            {
                "release_date": {"$regex": f"^{decade_start}|^{decade_start+1}|^{decade_end}"},
                "vote_average": {"$gt": 0},
                "vote_count": {"$gt": 0},
                "poster_path": {"$ne": None, "$ne": ""}
            },
            sort=[("vote_average", -1), ("vote_count", -1)],
            projection={"_id": 0, "title": 1, "vote_average": 1, "poster_path": 1}
        )


    
    def get_top_rated_movies(self, limit=5):
        return list(
            self.mongo.db.movies.find(
                {"vote_count": {"$gte": 500}, "poster_path": {"$ne": None}},
                {"_id": 0, "title": 1, "vote_average": 1, "vote_count": 1, "poster_path": 1}
            ).sort([("vote_average", -1), ("vote_count", -1)]).limit(limit)
        )
    
    def get_underrated_gems(self, limit=5):
        return list(
            self.mongo.db.movies.find(
                {"vote_average": {"$gte": 7}, "vote_count": {"$lte": 100}, "poster_path": {"$ne": None}},
                {"_id": 0, "title": 1, "vote_average": 1, "vote_count": 1, "poster_path": 1}
            ).sort("vote_average", -1).limit(limit)
        )
    
    def get_hottest_movies(self, limit=10):
        three_months_ago = datetime.now() - timedelta(days=90)

        return list(
            self.mongo.db.movies.find(
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