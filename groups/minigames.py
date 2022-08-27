# from enum import Enum, auto
from discord import app_commands as slash

import discord
import games
import json

from resources import add_friendship
from ui import MenuView



# class Leaderboard(Enum):
#     Slides = auto()
#     Slidess = auto()


# TODO: Implement currency for games, interacts with friendship level
class Game(slash.Group):

    # TODO: Refactor all games with an embed in views using a superclass to store both views and embeds
    @slash.command(description="Play a game of TicTacToe against a friend or against ME")
    async def tictactoe(self, interaction: discord.Interaction, opponent: discord.Member | None = None):
        add_friendship(interaction.user, (2 + int(not opponent)))
        if opponent is not None:
            add_friendship(opponent, 2.5)
        game = games.TicTacToeGame(interaction, opponent or interaction.client.user) # type: ignore
        await interaction.response.send_message(embed=game.embed, view=game.view)

    @slash.command(name='slide', description='Play a game of Slide Puzzle. Try it against ME at level 3, I challenge you')
    async def slide_puzzle(self, interaction: discord.Interaction, size: slash.Range[int, 3, 5]):
        add_friendship(interaction.user, 3)
        game = games.SlidesGame(interaction, size)
        await interaction.response.send_message(embed=game.embed, view=game.view)

    
    @slash.command(description='Play a roulette game.')
    async def roulette(self, interaction: discord.Interaction, choice: games.RouletteChoice) -> None:
        add_friendship(interaction.user, 1)
        game = games.RouletteGame(interaction, choice)
        await interaction.response.send_message(embed=game.embed, view=game.view)

    @slash.command(description='Play a slots game.')
    async def slots(self, interaction: discord.Interaction) -> None:
        add_friendship(interaction.user, 1.5)
        game = games.SlotsGame(interaction)
        await interaction.response.send_message(embed=game.embed)
        await game.run()
    
    @slash.command(description='Play a Black Jack game.')
    async def blackjack(self, interaction: discord.Interaction) -> None:
        add_friendship(interaction.user, 1)
        lobby = games.BJLobby(interaction)
        await lobby.run()
        game = games.BJGame(lobby)
        await game.run()

    def leaderboard(self, game: str):
        with open(f'games/{game}/leaderboard.json') as f:
            l = json.load(f)
        return l

    @slash.command(name='leaderboard', description='Shows the leaderboard of single player games')
    async def game_leaderboard(self, interaction: discord.Interaction): #, game: Leaderboard):
        # match game:
        #     case Leaderboard.Slides | Leaderboard.Slidess:
        l: dict[str, dict[str, dict[str, int]]] = self.leaderboard('slides')
        embeds: list[discord.Embed] = []
        for category in l.keys():
            if len(l[category]) == 0:
                continue
            embeds.append(discord.Embed(title='Slide Puzzle', description=category))
            for position in l[category]:
                player = l[category][position]
                if interaction.guild is not None:
                    user = await interaction.guild.fetch_member(player['user'])
                else:
                    user = await interaction.client.fetch_user(player['user'])
                embeds[-1].add_field(name=f'{position} • {user.display_name}', value=f'Number of moves: {player["score"]}', inline=False)

        view = MenuView(embeds)
        await interaction.response.send_message(embed=embeds[0], view=view)       