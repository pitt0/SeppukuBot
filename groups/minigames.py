# from enum import Enum, auto
from discord import app_commands as slash

import discord
import games

from games.leaderboard import Leaderboard
from resources import add_friendship
from ui import MenuView



# TODO: Implement currency for games, interacts with friendship level
class Game(slash.Group):

    @slash.command(description="Play a game of TicTacToe against a friend or against ME")
    async def tictactoe(self, interaction: discord.Interaction, opponent: discord.Member | None = None):
        add_friendship(interaction.user, (2 + int(not opponent)))
        if (opponent is not None):
            add_friendship(opponent, 2.5)
        game = games.TicTacToeGame(interaction, opponent or interaction.client.user) # type: ignore
        await interaction.response.send_message(embed=game.embed, view=game.view)

    @slash.command(name="slide", description="Play a game of Slide Puzzle.")
    async def slide_puzzle(self, interaction: discord.Interaction, size: slash.Range[int, 3, 5]):
        add_friendship(interaction.user, 3)
        game = games.SlidesGame(interaction, size)
        await interaction.response.send_message(embed=game.embed, view=game.view)

    @slash.command(description="Start a raffle")
    async def raffle(self, interaction: discord.Interaction, seconds: int):
        add_friendship(interaction.user, 1.5)
        game = games.RaffleGame(interaction, seconds)
        await game.run()
    
    @slash.command(description="Play a roulette game.")
    async def roulette(self, interaction: discord.Interaction) -> None:
        add_friendship(interaction.user, 1)
        game = games.RouletteGame()
        await interaction.response.send_message(embed=game.embed, view=game.view)

    @slash.command(description="Play a slots game.")
    async def slots(self, interaction: discord.Interaction) -> None:
        add_friendship(interaction.user, 1.5)
        game = games.SlotsGame(interaction)
        await interaction.response.send_message(embed=game.embed)
        await game.run()
    
    @slash.command(description="Play a Black Jack game.")
    async def blackjack(self, interaction: discord.Interaction) -> None:
        add_friendship(interaction.user, 1)
        game = games.BJGame(interaction)
        await game.run()

    @slash.command(name="leaderboard", description="Shows the leaderboard of single player games")
    async def game_leaderboard(self, interaction: discord.Interaction):
        lb = Leaderboard.load("slides")
        embeds: list[discord.Embed] = []
        for category in lb.keys():
            if len(lb[category]) == 0:
                continue
            embeds.append(discord.Embed(title="Slide Puzzle", description=category))
            for position in lb[category]:
                player = lb[category][position]
                if interaction.guild is not None:
                    user = await interaction.guild.fetch_member(player["user"])
                else:
                    user = await interaction.client.fetch_user(player["user"])
                embeds[-1].add_field(
                    name=f"{position} • {user.display_name}",
                    value=f"Number of moves: {player['score']}",
                    inline=False
                )

        view = MenuView(embeds)
        await interaction.response.send_message(embed=embeds[0], view=view)       