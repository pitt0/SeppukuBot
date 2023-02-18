from typing import NamedTuple


class Genre(NamedTuple):
    genre_id: int
    genre_name: str


class MovieCast(NamedTuple):
    movie_id: str
    person_id: str
    character_name: str | None
    cast_order: int | None


class Person(NamedTuple):
    person_id: int
    person_name: str


class MovieGenre(NamedTuple):
    movie_id: str
    genre_id: int


class Movie(NamedTuple):
    movie_id: str
    title: str
    homepage: str | None
    overview: str
    cover: str
    plot: str
    release_date: str
    runtime: int            # minutes
    rating: float
    vote_count: int