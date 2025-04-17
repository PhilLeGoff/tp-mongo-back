from datetime import datetime
from bson import ObjectId

class Actor:
    from datetime import datetime
from bson import ObjectId
from threading import Thread
import os
import requests


class Actor:
    @staticmethod
    def get_details(mongo, actor_id):
        actors_col = mongo.db.actors
        movies_col = mongo.db.movies

        actor = actors_col.find_one({"id": actor_id})
        TMDB_API_KEY = os.getenv("TMDB_API_KEY")
        TMDB_BASE = os.getenv("TMDB_BASE", "https://api.themoviedb.org/3")

        def enrich_database(data):
            try:
                processed_movies = []
                for movie in data.get("movie_credits", {}).get("cast", []):
                    existing = movies_col.find_one({"id": movie["id"]})
                    if existing:
                        processed_movies.append(existing["_id"])
                    else:
                        result = movies_col.insert_one(movie)
                        processed_movies.append(result.inserted_id)

                actor_doc = {
                    "id": data["id"],
                    "name": data["name"],
                    "biography": data.get("biography"),
                    "profile_path": data.get("profile_path"),
                    "birthday": data.get("birthday"),
                    "deathday": data.get("deathday"),
                    "popularity": data.get("popularity"),
                    "place_of_birth": data.get("place_of_birth"),
                    "movie_ids": processed_movies,
                    "updated_at": datetime.utcnow().timestamp()
                }

                if actor:
                    actors_col.update_one({"id": actor_id}, {"$set": actor_doc})
                else:
                    actors_col.insert_one(actor_doc)

            except Exception as e:
                print("❌ Failed to enrich actor in background:", e)

        # Populate movies if found in DB
        if actor and "movie_ids" in actor:
            actor["_id"] = str(actor["_id"])
            actor["movies"] = list(movies_col.find(
                {"_id": {"$in": actor.get("movie_ids", [])}},
                {"_id": 0, "title": 1, "poster_path": 1, "id": 1, "popularity": 1}
            ))
            actor["movies"].sort(key=lambda m: m.get("popularity", 0), reverse=True)
            actor["movies"] = actor["movies"][:20]
            return actor

        # Fallback: fetch from TMDB now
        print(f"ℹ️ Fetching actor {actor_id} from TMDB...")
        url = f"{TMDB_BASE}/person/{actor_id}"
        params = {
            "api_key": TMDB_API_KEY,
            "append_to_response": "movie_credits,images"
        }
        res = requests.get(url, params=params)
        if res.status_code != 200:
            print("❌ TMDB API Error:", res.status_code)
            return None

        data = res.json()

        movies = sorted(
            data.get("movie_credits", {}).get("cast", []),
            key=lambda m: m.get("popularity", 0),
            reverse=True
        )[:20]

        # Start enrichment thread
        Thread(target=lambda: enrich_database(data)).start()

        return {
            "id": data["id"],
            "name": data["name"],
            "biography": data.get("biography"),
            "profile_path": data.get("profile_path"),
            "birthday": data.get("birthday"),
            "deathday": data.get("deathday"),
            "popularity": data.get("popularity"),
            "place_of_birth": data.get("place_of_birth"),
            "movies": [
                {
                    "id": m["id"],
                    "title": m.get("title"),
                    "poster_path": m.get("poster_path"),
                    "popularity": m.get("popularity")
                }
                for m in movies
            ]
        }

