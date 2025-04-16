from bson import ObjectId
from collections import Counter

from app.models.genre import Genre


class GenreService:
    def __init__(self, mongo):
        self.mongo = mongo

    def get_genres(self):
        return Genre.get_all(self.mongo)

    def get_genre(self, genre_id):
        return Genre.get_by_id(self.mongo, ObjectId(genre_id))

    def get_most_common_genres(self, limit=10):
        all_movies = self.mongo.db.movies.find({}, {"genres": 1})

        genres = []
        for movie in all_movies:
            if "genres" in movie and isinstance(movie["genres"], list):
                for g in movie["genres"]:
                    if isinstance(g, dict) and "name" in g:
                        genres.append(g["name"])
                    elif isinstance(g, str):
                        genres.append(g)

        genre_counts = Counter(genres)
        sorted_genres = genre_counts.most_common(limit)

        return [{"name": g[0], "count": g[1]} for g in sorted_genres]
    
    def get_popular_movies_by_genre(self, genre_name, limit=10):
        query = {
            "genres": {
                "$elemMatch": {
                    "name": {"$regex": f"^{genre_name}$", "$options": "i"}
                }
            }
        }

        return list(
            self.mongo.db.movies.find(query, {"_id": 0})
            .sort("popularity", -1)
            .limit(limit)
        )