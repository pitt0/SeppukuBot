from discord import app_commands as slash
from enum import Enum, auto

import discord
import imdb as IMDb

import models
import ui

from resources.database import WatchList, Movies as MovieDB



class WL(Enum):
    Personal = auto()
    Server = auto()


class Movies(slash.Group):

    imdb: IMDb.IMDbBase = IMDb.IMDb()

    def __fetch_movie(self, title: str) -> list[models.Movie]:
        movies = []
        for movie in self.imdb.search_movie(title, results=5):
            movies.append(models.Movie.from_imdb(movie))

        return movies

    def watch_list(self, requester_id: int) -> list[models.Movie]:
        requester = str(requester_id)
        with WatchList() as wl:
            if requester not in wl:
                return []
            movies = [models.Movie.from_id(movieID) for movieID in wl[requester]]
        
        return movies

    def save_movie(self, requester_id: int, movie: models.Movie):
        requester = str(requester_id)
        with WatchList() as wl:
            if requester not in wl:
                wl[requester] = []
            wl[requester].append(movie.id)
        
        with MovieDB() as cur:
            cur.execute("""INSERT INTO Movies (ID, Title, Plot, Cast, Genres, Cover, Rating, Year) VALUES (?, ?, ?, ?, ?, ?, ?, ?);""", 
            (movie.id, movie.title, movie.plot, ','.join(movie.cast), ','.join(movie.genres), movie.cover, movie.rating, movie.year))

    def unsave_movie(self, requester_id: int, movie: models.Movie):
        requester = str(requester_id)
        with WatchList() as wl:
            if requester not in wl:
                wl[requester] = []
                return
            if movie.id in wl[requester]:
                wl[requester].remove(movie.id)

    @slash.command(name='search', description='Searches a movie or a series into the imdb database.')
    async def get_movie(self, interaction: discord.Interaction, title: str):
        await interaction.response.defer()
        movies = self.__fetch_movie(title)
        embeds = [movie.embed for movie in movies]
        v = ui.MenuView(embeds)
        await interaction.followup.send(embed=embeds[0], view=v)

    @slash.command(name='add', description='Adds a movie to a WatchList.')
    async def add_movie(self, interaction: discord.Interaction, title: str, watchlist: WL = WL.Personal, choose: bool = False):
        await interaction.response.defer()
        movies = self.__fetch_movie(title)
        if len(movies) == 0:
            embed = discord.Embed(
                title="Couldn't find anything :(", 
                description=f"Searching {title} returned no result.", 
                color=discord.Color.dark_red()
                )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return

        if choose:
            v = ui.MovieView(movies)
            await interaction.followup.send(embed=movies[0].embed, view=v)
            await v.wait()
            movie = v.movie
        else:
            movie = movies[0]

        match watchlist:
            case WL.Personal:
                requester = interaction.user
                person = 'your'
            case WL.Server if interaction.guild is None:
                requester = interaction.user
                person = 'your'
            case WL.Server if interaction.guild is not None:
                requester = interaction.guild
                person = "server's"
            case _:
                raise ValueError()

        self.save_movie(requester.id, movie)


        await interaction.followup.send(
            embed=discord.Embed(
                title='Movie Saved',
                description=f'{movie.title} has been saved to {person} WatchList',
                color=discord.Color.gold()
                )
            )
    
    @slash.command(name='watchlist', description='Sends the list of the movies in the a WatchList.')
    async def send_watchlist(self, interaction: discord.Interaction, watchlist: WL = WL.Personal):
        match watchlist:
            case WL.Personal:
                requester = interaction.user
                person = 'Your'
            case WL.Server if interaction.guild is None:
                requester = interaction.user
                person = 'Your'
            case WL.Server if interaction.guild is not None:
                requester = interaction.guild
                person = "Server's"
            case _:
                raise ValueError()

        await interaction.response.defer()

        movies = self.watch_list(requester.id)
        if len(movies) == 0:
            await interaction.followup.send(f'{person} WatchList is empty :(')
            return

        v = ui.WLView(movies, person)
        await interaction.followup.send(embed=v.embed, view=v)

    @slash.command(name='remove', description='Removes a movie from a WatchList')
    async def remove_movie(self, interaction: discord.Interaction, title: str, watchlist: WL = WL.Personal):
        movies = self.__fetch_movie(title)
        movie = movies[0]
        match watchlist:
            case WL.Personal:
                requester = interaction.user
                person = 'your'
            case WL.Server if interaction.guild is None:
                requester = interaction.user
                person = 'your'
            case WL.Server if interaction.guild is not None:
                requester = interaction.guild
                person = "server's"
            case _:
                raise ValueError()

        self.unsave_movie(requester.id, movie)
        await interaction.response.send_message(
            embed=discord.Embed(
                title='Movie Removed',
                description=f'{movie.title} has been removed from {person} WatchList',
                color=discord.Color.blue()
                )
            )

