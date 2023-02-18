from typing import Sequence
from typing import Self

import discord
import random

from games.leaderboard import Leaderboard
from games.utils import punish


class SlidesGame:

    def __init__(self, interaction: discord.Interaction, size: int) -> None:
        self.embed = discord.Embed(title="Game", description="Moves: 0", color=discord.Color.og_blurple())
        self.view = SlidePuzzle(interaction.user, self.embed)
        self.view.set_size(size)
    


class BTile(discord.ui.Button["SlidePuzzle"]):

    def __init__(self, label: str, x: int, y: int):
        super().__init__(label=label, row=y)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None

        if interaction.user != self.view.player:
            await punish(interaction, -1.2)
            return

        self.view.add_move()
        self.view.tiless.label, self.label = self.label, self.view.tiless.label
        self.view.tiless = self
        self.view.rearrange_buttons()

        if await self.view.check_win():
            await self.view.win(interaction)
        else:
            await interaction.response.edit_message(view=self.view)

    def is_near(self, button: Self) -> bool:
        return (
            not (self.x != button.x and self.y != button.y) and
            (
                (self.x == button.x - 1 or self.x == button.x + 1) or
                (self.y == button.y - 1 or self.y == button.y + 1)
            ) 
        )


class SlidePuzzle(discord.ui.View):

    children: list[BTile]
    leaderboard_path = "games/slides/leaderboard.json"

    def __init__(self, player: discord.User | discord.Member, embed: discord.Embed):
        super().__init__(timeout=None)
        
        self.player = player
        self.moves = 0

        self.embed = embed

    
    def set_size(self, size: int) -> None:
        items: list[str] = [str(num+1) for num in range((size**2)-1)]
        tiles: list[str] = [
            items.pop(random.randint(0, len(items)-1))
            for _ in range(len(items))
        ]
        
        while not self.solvable(tiles):
            random.shuffle(tiles)

        self.size = size
        for y in range(size):
            for x in range(size):
                if not (x == y == size-1):
                    tile = BTile(tiles.pop(0), x, y)
                    self.add_item(tile)
        
        self.tiless = BTile("\u200b", size-1, size-1)
        self.add_item(self.tiless)

    @staticmethod
    def solvable(tiles: Sequence[str]) -> bool:
        counter = 0
        for index, tile1 in enumerate(tiles[:-1]):
            for tile2 in tiles[index: ]:
                if int(tile1) > int(tile2):
                    counter += 1

        return counter % 2 == 0

    def rearrange_buttons(self) -> None:
        for index, button in enumerate(self.children):
            if button.label == str(index + 1):
                button.style = discord.ButtonStyle.green
            else:
                button.style = discord.ButtonStyle.grey

            button.disabled = not button.is_near(self.tiless)

    def add_move(self) -> None:
        self.moves += 1
        self.embed.description = f"Moves: {self.moves}"

    async def check_win(self) -> bool:
        items = tuple(str(num+1) for num in range(self.size*self.size))
        for index, child in enumerate(self.children):
            if not (items[index] == child.label or child.label == "\u200b"):
                return False
        return True

    async def end_game(self) -> None:
        for child in self.children:
            child.style = discord.ButtonStyle.green
            child.disabled = True

    async def win(self, interaction: discord.Interaction) -> None:
        await self.end_game()
        await interaction.response.edit_message(content="You won!", view=self)
        
        with Leaderboard("slides") as lb:
            mode = lb[f"{self.size}x{self.size}"]
            last = str(len(mode.keys()))

            entry = {
                "user": self.player.id,
                "score": self.moves
            }

            mode[last] = entry
            rank = 0 # it could be possiby unbound out of the for
            
            for rank in mode[::-1]:
                above = str(int(rank) - 1)
                if (mode[rank]["score"] < mode[above]["score"]):
                    mode[rank], mode[above] = mode[above], mode[rank]
            
        if (int(rank) <= 10):
            await interaction.followup.send(
                f"Congratulations {self.player.mention}! You are now in the leaderboard!\n" +
                "Use `/game leaderboard [game: slides]` to see it!"
            )