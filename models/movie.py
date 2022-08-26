from dataclasses import dataclass
from typing_extensions import Self

import discord
import imdb

from resources.database import Movies


@dataclass
class Movie:

    id: str
    title: str
    plot: str
    cast: list[str]
    genres: list[str]
    cover: str
    rating: int | str
    year: int | str


    def __post_init__(self) -> None:
        embed = discord.Embed(title=self.title, description=self.plot, color=discord.Color.orange())
        embed.add_field(name='Cast', value=', '.join(self.cast))
        embed.add_field(name='Genres', value=', '.join(self.genres), inline=False)
        embed.set_thumbnail(url=self.cover)
        embed.add_field(name='Rating', value=self.rating)
        embed.add_field(name='Year', value=self.year)
        
        self.embed = embed

    @classmethod
    def from_id(cls, id: str) -> Self:
        with Movies() as cur:
            cur.execute("SELECT * FROM Movies WHERE ID=?", (id,))
            movie = cur.fetchone()
            if movie is None:
                db = imdb.IMDb()
                movie = db.get_movie(id)
                return cls.from_imdb(movie)
            
            return cls(*movie)

    @classmethod
    def from_db(cls, id: str, movie: list) -> Self:
        self = cls(id, *movie)
        return self


    @classmethod
    def from_imdb(cls, movie: imdb.Movie.Movie) -> Self:

        data = {
            'id': movie.getID(),
            'title': str(movie.get('title', 'Unknown')),
            'plot': movie.get('plot', ['-'])[0],
            'genres': movie.get('genre', ['-']),
            'cover': str(movie.get('cover url', 'http://127.0.0.1')),
            'rating': movie.get('rating', '-'),
            'year': movie.get('year', '-')
        }

        cast = []
        if movie.get('cast'):
            for actor in movie['cast'][: 5]:
                cast.append(actor.get('name'))
        else:
            cast.append('-')
        
        self = cls(**data)
        return self
