from bson import ObjectId
from datetime import datetime, timedelta
from collections import Counter


class Movie:
    @staticmethod
    def create(mongo, data):
        data['created_at'] = datetime.utcnow()
        return mongo.db.movies.insert_one(data)

    @staticmethod
    def get_all(mongo):
        return list(mongo.db.movies.find().limit(50))

    @staticmethod
    def get_by_id(mongo, movie_id):
        return mongo.db.movies.find_one({"_id": movie_id})

    @staticmethod
    def get_latest(mongo, limit=10):
        return list(mongo.db.movies.find(
            {"release_date": {"$exists": True, "$ne": ""}},
            {"_id": 0}
        ).sort("release_date", -1).limit(limit))

    @staticmethod
    def get_popular(mongo):
        return mongo.db.movies.find().sort("popularity", -1).limit(10)

    @staticmethod
    def get_all_cursor(mongo, last_id=None, per_page=10):
        query = {}
        if last_id:
            query = {"_id": {"$gt": ObjectId(last_id)}}
        return mongo.db.movies.find(query).sort("_id", 1).limit(per_page)

    @staticmethod
    def get_title_frequency(mongo):
        titles = mongo.db.movies.distinct("title")
        words = []
        excluded = {"the", "a", "an", "of", "-", "_", "and", "in", "to", "de", "&"}
        for title in titles:
            words.extend([w for w in title.split() if w.lower() not in excluded])
        return Counter(words).most_common(1)

    @staticmethod
    def get_popular_movies(mongo, limit=10):
        return list(mongo.db.movies.find({}, {"_id": 0}).sort("popularity", -1).limit(limit))

    @staticmethod
    def get_top_rated_movies(mongo, limit=10):
        return list(mongo.db.movies.find(
            {"poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "vote_average": 1, "poster_path": 1, "id": 1}
        ).sort("vote_average", -1).limit(limit))

    @staticmethod
    def get_underrated_gems(mongo, limit=20):
        return list(mongo.db.movies.find(
            {"vote_average": {"$gte": 7}, "vote_count": {"$lte": 100}, "poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "vote_average": 1, "vote_count": 1, "poster_path": 1, "id": 1}
        ).sort("vote_average", -1).limit(limit))

    @staticmethod
    def get_hottest_movies(mongo, limit=10):
        three_months_ago = datetime.now() - timedelta(days=90)
        return list(mongo.db.movies.find(
            {
                "release_date": {"$gte": three_months_ago.strftime("%Y-%m-%d")},
                "vote_count": {"$gte": 100},
                "vote_average": {"$gte": 6.0},
                "poster_path": {"$ne": None}
            },
            {"_id": 0, "title": 1, "vote_average": 1, "vote_count": 1, "release_date": 1, "poster_path": 1, "id": 1}
        ).sort([("vote_average", -1), ("vote_count", -1)]).limit(limit))

    @staticmethod
    def get_most_appreciated_genres(mongo, limit=10):
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
        decade_start = int(decade[:-1])
        decade_end = decade_start + 9
        return mongo.db.movies.find_one(
            {
                "release_date": {"$regex": f"^{decade_start}|^{decade_start+1}|^{decade_end}"},
                "vote_average": {"$gt": 0},
                "vote_count": {"$gt": 0},
                "poster_path": {"$ne": None, "$ne": ""}
            },
            sort=[("vote_average", -1), ("vote_count", -1)],
            projection={"_id": 0, "title": 1, "vote_average": 1, "poster_path": 1}
        )

    @staticmethod
    def get_new_releases(mongo):
        return list(mongo.db.movies.find(
            {"release_date": {"$exists": True, "$ne": ""}},
            {"_id": 0, "title": 1, "poster_path": 1, "release_date": 1, "id": 1}
        ).sort("release_date", -1).limit(15))

    @staticmethod
    def get_most_popular(mongo):
        return list(mongo.db.movies.find(
            {"poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1, "popularity": 1, "id": 1}
        ).sort("popularity", -1).limit(15))

    @staticmethod
    def get_critically_acclaimed(mongo):
        return list(mongo.db.movies.find(
            {"vote_average": {"$gte": 8}, "vote_count": {"$gt": 1000}},
            {"_id": 0, "title": 1, "poster_path": 1, "vote_average": 1, "id": 1}
        ).sort("vote_average", -1).limit(15))

    @staticmethod
    def get_long_movies(mongo):
        return list(mongo.db.movies.find(
            {"runtime": {"$gte": 150}, "poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1, "runtime": 1, "id": 1}
        ).limit(15))

    @staticmethod
    def get_short_movies(mongo):
        return list(mongo.db.movies.find(
            {"runtime": {"$lte": 90}, "poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1, "runtime": 1, "id": 1}
        ).limit(15))

    @staticmethod
    def get_movies_by_decade(mongo, start_year):
        return list(mongo.db.movies.find(
            {"release_date": {"$regex": f"^{start_year}"}},
            {"_id": 0, "title": 1, "poster_path": 1, "id": 1, "vote_average": 1, "vote_count": 1}
        ).limit(15))
    @staticmethod
    def get_best_french_movies(mongo, limit=10):
        return list(
            mongo.db.movies.find(
                {
                    "original_language": "fr",
                    "vote_count": {"$gte": 100},
                    "poster_path": {"$ne": None}
                },
                {"_id": 0, "title": 1, "poster_path": 1, "vote_average": 1, "id": 1}
            ).sort([("vote_average", -1), ("vote_count", -1)]).limit(limit)
        )

    @staticmethod
    def get_best_action_movies(mongo, limit=10):
        return list(
            mongo.db.movies.find(
                {
                    "genres.name": "Action",
                    "vote_count": {"$gte": 100},
                    "poster_path": {"$ne": None}
                },
                {"_id": 0, "title": 1, "poster_path": 1, "vote_average": 1, "id": 1}
            ).sort([("vote_average", -1), ("vote_count", -1)]).limit(limit)
        )

    @staticmethod
    def get_movies_from_90s(mongo, limit=15):
        return list(
            mongo.db.movies.find(
                {
                    "release_date": {
                        "$regex": "^199[0-9]"  # matches 1990 to 1999
                    }
                },
                {"_id": 0, "title": 1, "poster_path": 1, "id": 1}
            ).sort("release_date", 1).limit(limit)
        )

    @staticmethod
    def get_movies_by_genre(mongo, genre_name):
        return list(mongo.db.movies.find(
            {"genres.name": genre_name, "poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1, "id": 1}
        ).limit(15))

    @staticmethod
    def get_true_stories(mongo):
        return list(mongo.db.movies.find(
            {"overview": {"$regex": "true story", "$options": "i"}},
            {"_id": 0, "title": 1, "poster_path": 1, "id": 1}
        ).limit(15))

    @staticmethod
    def get_best_movies_per_decade(mongo):
        pipeline = [
            {
                "$match": {
                    "release_date": {"$exists": True, "$ne": ""},
                    "vote_average": {"$gt": 0},
                    "vote_count": {"$gt": 50}
                }
            },
            {
                "$addFields": {
                    "year": {"$toInt": {"$substr": ["$release_date", 0, 4]}}
                }
            },
            {
                "$addFields": {
                    "decade": {
                        "$concat": [
                            {"$toString": {"$multiply": [{"$floor": {"$divide": ["$year", 10]}}, 10]}},
                            "s"
                        ]
                    }
                }
            },
            {
                "$sort": {"vote_average": -1, "vote_count": -1}
            },
            {
                "$group": {
                    "_id": "$decade",
                    "movie": {"$first": "$$ROOT"}
                }
            },
            {
                "$replaceRoot": {"newRoot": "$movie"}
            },
            {
                "$project": {
                    "_id": 0,
                    "id": 1,
                    "title": 1,
                    "vote_average": 1,
                    "vote_count": 1,
                    "poster_path": 1,
                    "release_date": 1
                }
            },
            {
                "$sort": {"release_date": 1}
            }
        ]

        return list(mongo.db.movies.aggregate(pipeline))

    @staticmethod
    def search_movies(mongo, keyword, genre, page, limit):
        pipeline = []
        # print(genre)

        if keyword:
            pipeline.append({
                "$match": {
                    "title": {
                        "$regex": keyword,
                        "$options": "i"
                    }
                }
            })

        if genre:
            pipeline.append({
                "$match": {
                    "genres.name": genre
                    # "genre_ids": genre_id
                }
            })
        
        print(genre)

        # Count total results
        count_pipeline = pipeline.copy()
        count_pipeline.append({"$count": "total"})
        total_result = list(mongo.db.movies.aggregate(count_pipeline))
        total = total_result[0]['total'] if total_result else 0
        print(total_result)
        # Pagination logic
        skip = (page - 1) * limit
        pipeline.append({"$skip": skip})
        pipeline.append({"$limit": limit})

        movies = list(mongo.db.movies.aggregate(pipeline))

        return {
            "results": movies,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
