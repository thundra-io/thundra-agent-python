from .movie import Movie

# throw exceptions whose names are starts with "Demo" if you do not want to be notified
class DemoException(Exception):
    pass

class MovieRepository:

     def __init__(self):
         self.movies = {
             0: Movie("The Shawshank Redemption ", "Frank Darabont", 1994),
             1: Movie("The Godfather", "Francis Ford Coppola", 1972),
             2: Movie("The Dark Knight", "Christopher Nolan", 2008),
             3: Movie("The Godfather: Part II", "Francis Ford Coppola", 1974),
             4: Movie("Pulp Fiction", "Quentin Tarantino", 1994),
             5: Movie("Schindler's List", "Steven Spielberg", 1993),
             6: Movie("The Lord of the Rings: The Return of the King", "Peter Jackson", 2003),
             7: Movie("The Good, the Bad and the Ugly", "Sergio Leone", 1966),
             8: Movie("12 Angry Men", "Sidney Lumet", 1957),
             9: Movie("Forrest Gump", "Robert Zemeckis", 1994)
         }

         self.number_of_movies = 10

     def find_movie(self, id):
         if id >= 10:
             raise DemoException("No movie is found")
         return self.movies[id] if id in self.movies else None