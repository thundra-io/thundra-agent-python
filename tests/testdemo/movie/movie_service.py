from .movie_repository import MovieRepository

class MovieService:

    def __init__(self):
        self.movie_repository = MovieRepository()

    def get_movie(self, id):
        return self.movie_repository.find_movie(id)