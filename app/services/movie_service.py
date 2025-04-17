from bson import ObjectId
from datetime import datetime, timedelta
import os
from collections import Counter

from app.models.movie import Movie
import os
import requests
from threading import Thread

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "d24585bf3900cb0543080519e65e9d15")
TMDB_BASE = os.getenv("TMDB_BASE", "https://api.themoviedb.org/3")


class MovieService:
    def __init__(self, mongo):
        self.mongo = mongo

    def get_movies(self):
        return Movie.get_all(self.mongo)

    def get_movie(self, movie_id):
        return Movie.get_by_id(self.mongo, movie_id)

    def get_popular_movies(self, limit=10):
        return Movie.get_popular_movies(self.mongo, limit)

    def get_latest_movies(self, limit=10):
        return Movie.get_latest(self.mongo, limit)

    def get_top_rated_movies(self, limit=10):
        return Movie.get_top_rated_movies(self.mongo, limit)

    def get_most_appreciated_genres(self, limit=5):
        return Movie.get_most_appreciated_genres(self.mongo, limit)

    def get_best_movies_by_decade(self):
        return Movie.get_best_movies_by_decade(self.mongo)

    def get_available_decades(self):
        return Movie.get_available_decades(self.mongo)

    def get_best_movie_for_decade(self, decade):
        return Movie.get_best_movie_for_decade(self.mongo, decade)

    def get_underrated_gems(self, limit=20):
        return Movie.get_underrated_gems(self.mongo, limit)

    def get_hottest_movies(self, limit=10):
        return Movie.get_hottest_movies(self.mongo, limit)

    def get_new_releases(self):
        return Movie.get_new_releases(self.mongo)

    def get_most_popular(self):
        return Movie.get_most_popular(self.mongo)

    def get_critically_acclaimed(self):
        return Movie.get_critically_acclaimed(self.mongo)

    def get_best_french_movies(self, limit=10):
        return Movie.get_best_french_movies(self.mongo, limit)

    def get_best_action_movies(self, limit=10):
        return Movie.get_best_action_movies(self.mongo, limit)

    def get_movies_from_90s(self, limit=15):
        return Movie.get_movies_from_90s(self.mongo, limit)

    def get_best_movies_by_decade(self, start_year):
        return Movie.get_movies_by_decade(self.mongo, start_year)

    def get_movies_by_genre(self, genre_name):
        return Movie.get_movies_by_genre(self.mongo, genre_name)

    def get_true_stories(self):
        return Movie.get_true_stories(self.mongo)

    def get_title_frequency(self):
        return Movie.get_title_frequency(self.mongo)

    def get_movies_cursor(self, last_id=None, per_page=10):
        return Movie.get_all_cursor(self.mongo, last_id, per_page)

    def get_detailed_movie(self, movie_id):
        try:
            movies_col = self.mongo.db.movies
            actors_col = self.mongo.db.actors

            def ensure_actor(actor_data):
                existing = actors_col.find_one({"id": actor_data["id"]})
                if existing:
                    return existing["_id"]
                actor_doc = {
                    "id": actor_data["id"],
                    "name": actor_data["name"],
                    "profile_path": actor_data.get("profile_path"),
                    "popularity": actor_data.get("popularity"),
                    "known_for_department": actor_data.get("known_for_department"),
                    "fetched_at": datetime.utcnow()
                }
                inserted = actors_col.insert_one(actor_doc)
                return inserted.inserted_id

            def populate_actor_refs(actor_ids):
                return list(actors_col.find(
                    {"_id": {"$in": actor_ids}},
                    {"_id": 0, "id": 1, "name": 1, "profile_path": 1, "popularity": 1, "known_for_department": 1}
                ))

            # 🧠 Check DB first
            movie = movies_col.find_one({"id": movie_id})

            # If enriched already, populate & return
            if movie and "credits" in movie and isinstance(movie["credits"].get("cast"), list):
                cast_list = movie["credits"].get("cast", [])
                # Ensure that no out-of-range error happens when slicing
                if len(cast_list) > 6:
                    movie["credits"]["cast"] = populate_actor_refs(cast_list[:6])
                else:
                    movie["credits"]["cast"] = populate_actor_refs(cast_list)
                return movie


            # 🧪 Fetch from TMDB directly
            print(f"🔄 Fetching movie {movie_id} from TMDB...")
            url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            params = {
                "api_key": os.getenv("TMDB_API_KEY"),
                "append_to_response": "credits,videos"
            }
            res = requests.get(url, params=params)
            if res.status_code != 200:
                print("TMDB API error:", res.status_code)
                return None

            data = res.json()

            # Prepare return value with cast/crew populated (not ObjectIds)
            movie_response = {
                "id": data["id"],
                "title": data.get("title"),
                "overview": data.get("overview"),
                "release_date": data.get("release_date"),
                "poster_path": data.get("poster_path"),
                "backdrop_path": data.get("backdrop_path"),
                "vote_average": data.get("vote_average"),
                "vote_count": data.get("vote_count"),
                "original_language": data.get("original_language"),
                "genres": data.get("genres", []),
                "runtime": data.get("runtime"),
                "popularity": data.get("popularity"),
                "videos": data.get("videos", {}),
                "credits": {
                    "cast": data["credits"].get("cast", [])[:6],
                    "crew": data["credits"].get("crew", [])
                }
            }

            # 🧵 Enrich DB in background
            def enrich_database():
                try:
                    cast_ids = [ensure_actor(actor) for actor in data["credits"].get("cast", [])]
                    crew_ids = [ensure_actor(actor) for actor in data["credits"].get("crew", [])]

                    update_data = {
                        "credits": {"cast": cast_ids, "crew": crew_ids},
                        "videos": data.get("videos", {}),
                        "runtime": data.get("runtime"),
                        "fetched_at": datetime.utcnow()
                    }

                    if not movie:
                        update_data.update({
                            "id": data["id"],
                            "title": data.get("title"),
                            "overview": data.get("overview"),
                            "release_date": data.get("release_date"),
                            "poster_path": data.get("poster_path"),
                            "backdrop_path": data.get("backdrop_path"),
                            "vote_average": data.get("vote_average"),
                            "vote_count": data.get("vote_count"),
                            "original_language": data.get("original_language"),
                            "genres": data.get("genres", []),
                            "popularity": data.get("popularity"),
                        })
                        movies_col.insert_one(update_data)
                    else:
                        movies_col.update_one({"id": movie_id}, {"$set": update_data})

                except Exception as e:
                    print("❌ Background enrich failed:", e)

            Thread(target=enrich_database).start()

            return movie_response

        except Exception as e:
            print("❌ Error in get_detailed_movie:", e)
            return None

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