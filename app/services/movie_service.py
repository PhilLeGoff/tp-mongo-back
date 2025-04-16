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

    def get_popular_movies(self, limit=10):
        return Movie.get_popular_movies(self.mongo, limit)

    def get_latest_movies(self, limit=10):
        return Movie.get_latest(self.mongo, limit)

    def get_top_rated_movies(self, limit=10):
        return Movie.get_top_rated_movies(self.mongo, limit)

    def get_most_appreciated_genres(self, limit=5):
        return Movie.get_most_appreciated_genres(self.mongo, limit)

    def get_best_movies_by_decade(self):
        decades = Movie.get_available_decades(self.mongo)
        results = []

        for decade in decades:
            movie = Movie.get_best_movie_for_decade(self.mongo, decade)
            if movie:
                # Ajoute la décennie directement dans le titre
                movie["title"] = f"{movie['title']} ({decade})"
                results.append({
                    "decade": decade,
                    "movie": movie
                })

        return results

    def get_available_decades(self):
        return Movie.get_available_decades(self.mongo)

    def get_best_movie_for_decade(self, decade):
        return Movie.get_best_movie_for_decade(self.mongo, decade)

    def get_top_rated_movies(self, limit=5):
        return Movie.get_top_rated_movies(self.mongo, limit)

    def get_underrated_gems(self, limit=20):
        return Movie.get_underrated_gems(self.mongo, limit)

    def get_hottest_movies(self, limit=10):
        return Movie.get_hottest_movies(self.mongo, limit)

    def get_latest(self):
        return Movie.get_latest(self.mongo)

    def get_popular(self):
        return Movie.get_popular(self.mongo)

    #cursor based pagination
    def get_movies_cursor(self, last_id=None, per_page=10):
        return Movie.get_all_cursor(self.mongo, last_id, per_page)

    def get_title_frequency(self):
        return Movie.get_title_frequency(self.mongo)

    def get_new_releases(self):
        return list(self.mongo.db.movies.find(
            {"release_date": {"$exists": True, "$ne": ""}},
            {"_id": 0, "title": 1, "poster_path": 1, "release_date": 1}
        ).sort("release_date", -1).limit(15))

    def get_most_popular(self):
        return list(self.mongo.db.movies.find(
            {"poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1, "popularity": 1}
        ).sort("popularity", -1).limit(15))

    def get_critically_acclaimed(self):
        return list(self.mongo.db.movies.find(
            {"vote_average": {"$gte": 8}, "vote_count": {"$gt": 1000}},
            {"_id": 0, "title": 1, "poster_path": 1, "vote_average": 1}
        ).sort("vote_average", -1).limit(15))

    def get_long_movies(self):
        return list(self.mongo.db.movies.find(
            {"runtime": {"$gte": 150}, "poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1, "runtime": 1}
        ).limit(15))

    def get_short_movies(self):
        return list(self.mongo.db.movies.find(
            {"runtime": {"$lte": 90}, "poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1, "runtime": 1}
        ).limit(15))

    def get_movies_by_decade(self, start_year):
        return list(self.mongo.db.movies.find(
            {"release_date": {"$regex": f"^{start_year}"}},
            {"_id": 0, "title": 1, "poster_path": 1}
        ).limit(15))

    def get_movies_by_genre(self, genre_name):
        return list(self.mongo.db.movies.find(
            {"genres.name": genre_name, "poster_path": {"$ne": None}},
            {"_id": 0, "title": 1, "poster_path": 1}
        ).limit(15))

    def get_true_stories(self):
        return list(self.mongo.db.movies.find(
            {"overview": {"$regex": "true story", "$options": "i"}},
            {"_id": 0, "title": 1, "poster_path": 1}
        ).limit(15))

