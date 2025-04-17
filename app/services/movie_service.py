from bson import ObjectId
from datetime import datetime, timedelta
from collections import Counter

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
        return Movie.get_new_releases(self.mongo)

    def get_most_popular(self):
        return Movie.get_most_popular(self.mongo)

    def get_critically_acclaimed(self):
        return Movie.get_critically_acclaimed(self.mongo)

    def get_long_movies(self):
        return Movie.get_long_movies(self.mongo)

    def get_short_movies(self):
        return Movie.get_short_movies(self.mongo)

    def get_movies_by_decade(self, start_year):
        return Movie.get_movies_by_decade(self.mongo, start_year)

    def get_movies_by_genre(self, genre_name):
        return Movie.get_movies_by_genre(self.mongo, genre_name)

    def get_true_stories(self):
        return Movie.get_true_stories(self.mongo)
    
    def get_recommendations(self, user_ip, limit=15):
        favorites = list(self.mongo.db.favorites.find({"ip": user_ip}))
        if not favorites:
            return []

        genre_counter = Counter()

        for fav in favorites:
            movie = self.get_movie(fav["movie_id"])
            if movie and "genres" in movie:
                for g in movie["genres"]:
                    genre_name = g["name"] if isinstance(g, dict) else g
                    genre_counter[genre_name] += 1

        if not genre_counter:
            return []

        top_genres = [g for g, _ in genre_counter.most_common(2)]

        query = {
            "genres": {"$elemMatch": {"name": {"$in": top_genres}}},
            "vote_average": {"$gte": 7.0}
        }

        return list(self.mongo.db.movies.find(
            query,
            {"_id": 0, "title": 1, "poster_path": 1, "vote_average": 1}
        ).sort("vote_average", -1).limit(limit))

