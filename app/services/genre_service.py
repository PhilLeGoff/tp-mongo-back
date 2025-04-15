from bson import ObjectId

from app.models.genre import Genre


class GenreService:
    def __init__(self, mongo):
        self.mongo = mongo

    def get_genres(self):
        return Genre.get_all(self.mongo)

    def get_genre(self, genre_id):
        return Genre.get_by_id(self.mongo, ObjectId(genre_id))
