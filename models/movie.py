from functools import cached_property
from list_ext import List
from typing import Any, Self

import discord
import imdb

from .database import Movie as MovieEntry
from resources.database import Movies


class Movie:
    
    _data: Any
    _cast: list[str]
    _genres: list[str]

    def __init__(self, data: Any, cast: list[str], genres: list[str]):
        self._data = data
        self._cast = cast[:5]
        self._genres = genres

    @cached_property
    def cast(self) -> str:
        return ", ".join(str(person) for person in self._cast)
    
    @cached_property
    def genres(self) -> str:
        print(self._genres)
        return ", ".join(self._genres)
    

    @cached_property
    def _runtime(self) -> int:
        raise NotImplementedError
    
    @cached_property
    def _rating(self) -> float:
        raise NotImplementedError
    
    @cached_property
    def _vote_count(self) -> int:
        raise NotImplementedError
    
    
    @cached_property
    def id(self) -> str:
        raise NotImplementedError

    @cached_property
    def title(self) -> str:
        raise NotImplementedError
    
    @cached_property
    def overview(self) -> str:
        raise NotImplementedError
    
    @cached_property
    def cover(self) -> str:
        raise NotImplementedError
    
    @cached_property
    def plot(self) -> str:
        raise NotImplementedError
    
    @cached_property
    def release_date(self) -> str:
        raise NotImplementedError
    
    @cached_property
    def runtime(self) -> str:
        raise NotImplementedError
    
    @cached_property
    def rating(self) -> str:
        raise NotImplementedError
    

    @cached_property
    def embed(self) -> discord.Embed:
        return discord.Embed(
            title=self.title,
            description=self.plot,
            color=discord.Colour.orange()
        )\
        .add_field(name="Cast", value=self.cast)\
        .add_field(name="Genres", value=self.genres, inline=False)\
        .add_field(name="Rating", value=self.rating)\
        .add_field(name="Released", value=self.release_date)\
        .add_field(name="Rating", value=self.runtime)\
        .set_thumbnail(url=self.cover)
    
    def missing(self, cast: list[str]) -> list[str]:
        n = self._cast.copy()
        for person in cast:
            n.remove(person)
        return n

    def add_people(self, cur, cast: list[str]) -> None:
        if len(cast) < len(self._cast):
            n = self.missing(cast)
            _imdb = imdb.IMDb()
            for person in n:
                p_id = _imdb.search_person(person)[0].getID()
                cur.execute("INSERT INTO person (person_id, person_name) VALUES (?, ?);", (p_id, person))

    def upload(self) -> None:
        with Movies() as cur:
            cur.execute("INSERT INTO movie (movie_id, title, overview, cover, plot, release_date, runtime, rating, vote_count) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);",
                        (self.id, self.title, self.overview, self.cover, self.plot, self.release_date, self._runtime, self._rating, self._vote_count))
            
            g = ", ".join(f"'{genre}'" for genre in self._genres)
            cur.execute(f"SELECT genre_id FROM genre WHERE genre_name IN ({g});")
            genres = cur.fetchall()
            for genre in genres:
                cur.execute("INSERT INTO movie_genres (movie_id, genre_id) VALUES (?, ?);", (self.id, genre[0]))

            c = ", ".join(f"'{person}'" for person in self._cast)
            cur.execute(f"SELECT person_id FROM person WHERE person_name in ({c});")
            cast = cur.fetchall()
            self.add_people(cur, cast)
            for person in cast:
                cur.execute("INSERT INTO movie_cast (movie_id, person_id) VALUES (?, ?);", (self.id, person[0]))
    


class DBMovie(Movie):

    _data: MovieEntry


    @cached_property
    def _runtime(self) -> int:
        return self._data.runtime
    
    @cached_property
    def _rating(self) -> float:
        return self._data.rating
    
    @cached_property
    def _vote_count(self) -> int:
        return self._data.vote_count


    @cached_property
    def id(self) -> str:
        return self._data.movie_id

    @cached_property
    def title(self) -> str:
        return self._data.title
    
    @cached_property
    def overview(self) -> str:
        if self._data.overview != "-":
            return self._data.overview
        return self._data.plot
    
    @cached_property
    def cover(self) -> str:
        return self._data.cover
    
    @cached_property
    def plot(self) -> str:
        if self._data.plot != "-":
            return self._data.plot
        return self._data.overview
    
    @cached_property
    def release_date(self) -> str:
        return self._data.release_date
    
    @cached_property
    def runtime(self) -> str:
        if self._data.runtime < 60:
            return f"{self._data.runtime}m"
        
        h = self._data.runtime // 60
        r = self._data.runtime - (h * 60)
        return f"{h}h {r}m"
    
    @cached_property
    def rating(self) -> str:
        return f":star:{self._data.rating} ({self._data.vote_count})"
    

    @classmethod
    def load(cls, movie_id: str) -> Movie:
        with Movies() as cur:
            cur.execute("SELECT * FROM movie WHERE movie_id=?;", (movie_id,))
            data: MovieEntry | None = cur.fetchone()
            if data is None:
                return IMDBMovie.load(movie_id)
            cur.execute("SELECT person_name FROM person WHERE person_id=(SELECT person_id FROM movie_cast WHERE movie_id=?);", (movie_id,))
            cast: List[tuple[str]] = List(cur.fetchall())
            cur.execute("SELECT genre_name FROM genre WHERE genre_id=(SELECT genre_id FROM movie_genres WHERE movie_id=?);", (movie_id,))
            genres: List[tuple[str]] = List(cur.fetchall())

        return cls(MovieEntry(*data), cast.select(lambda t: t[0]), genres.select(lambda t: t[0]))
    

class IMDBMovie(Movie):

    _data: imdb.Movie.Movie


    @cached_property
    def _runtime(self) -> int:
        return self._data.get("runtimes", [0])[0]
    
    @cached_property
    def _rating(self) -> float:
        return self._data.get("rating", 0) # type: ignore

    @cached_property
    def _vote_count(self) -> int:
        return self._data.get("votes", 0) # type: ignore
    

    @cached_property
    def id(self) -> str:
        return str(self._data["imdbID"])

    @cached_property
    def title(self) -> str:
        return str(self._data.get("title", "Unknown"))
    
    @cached_property
    def overview(self) -> str:
        return str(self._data.get("plot outline", "-"))

    @cached_property
    def cover(self) -> str:
        return str(self._data.get("cover url", "http://217.0.0.1"))
    
    @cached_property
    def plot(self) -> str:
        return str(self._data.get("plot outline", "-"))
    
    @cached_property
    def release_date(self) -> str:
        return str(self._data.get("year", "-"))
    
    @cached_property
    def runtime(self) -> str:
        return str(self._data.get("runtimes", ["-"])[0])
    
    @cached_property
    def rating(self) -> str:
        return f":star:{self._rating} ({self._vote_count})"
    
    @classmethod
    def load(cls, movie_id: str) -> Self:
        _imdb = imdb.IMDb()
        movie = _imdb.get_movie(movie_id)
        return cls(movie, movie.get("cast", ["-"]), movie.get("genre", ["-"])) # type: ignore
    
    @classmethod
    def search(cls, query: str, results: int = 1) -> List[Self]:
        _imdb = imdb.IMDb()
        movies = _imdb.search_movie(query, results=results)
        return List(cls.load(movie.getID()) for movie in movies) # type: ignore