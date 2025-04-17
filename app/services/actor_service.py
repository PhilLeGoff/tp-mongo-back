import requests
from datetime import datetime
from bson import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE = os.getenv("TMDB_BASE", "https://api.themoviedb.org/3")

class ActorService:
    def __init__(self, mongo):
        self.mongo = mongo

    def get_actor_details(self, actor_id):
        try:
            actors_col = self.mongo.db.actors
            movies_col = self.mongo.db.movies

            # Try from DB first
            actor = actors_col.find_one({"id": actor_id})
            if actor:
                print("✅ actor found in DB")
                actor["_id"] = str(actor["_id"])

                # Populate movies
                movies = list(movies_col.find(
                    {"_id": {"$in": actor.get("movie_ids", [])}},
                    {"_id": 0, "title": 1, "poster_path": 1, "id": 1, "popularity": 1}
                ))
                movies.sort(key=lambda m: m.get("popularity", 0), reverse=True)
                actor["movies"] = movies[:20]
                return actor

            # Fetch from TMDB
            print("ℹ️ actor not in DB, fetching from TMDB...")
            url = f"{TMDB_BASE}/person/{actor_id}"
            params = {
                "api_key": TMDB_API_KEY,
                "append_to_response": "movie_credits,images"
            }
            res = requests.get(url, params=params)
            if res.status_code != 200:
                return None

            data = res.json()

            # Process movies: insert missing ones
            processed_movie_ids = []
            for movie in data.get("movie_credits", {}).get("cast", []):
                existing = movies_col.find_one({"id": movie["id"]})
                if existing:
                    processed_movie_ids.append(existing["_id"])
                else:
                    result = movies_col.insert_one(movie)
                    processed_movie_ids.append(result.inserted_id)

            actor_doc = {
                "id": data["id"],
                "name": data["name"],
                "biography": data.get("biography"),
                "profile_path": data.get("profile_path"),
                "birthday": data.get("birthday"),
                "deathday": data.get("deathday"),
                "popularity": data.get("popularity"),
                "movie_ids": processed_movie_ids,
                "updated_at": datetime.utcnow().timestamp()
            }

            insert_result = actors_col.insert_one(actor_doc)
            actor_doc["_id"] = str(insert_result.inserted_id)

            # Populate movies for frontend
            actor_doc["movies"] = list(movies_col.find(
                {"_id": {"$in": processed_movie_ids}},
                {"_id": 0, "title": 1, "poster_path": 1, "id": 1, "popularity": 1}
            ))
            actor_doc["movies"].sort(key=lambda m: m.get("popularity", 0), reverse=True)
            actor_doc["movies"] = actor_doc["movies"][:20]

            return actor_doc

        except Exception as e:
            print("❌ Error fetching actor details:", e)
            return None
