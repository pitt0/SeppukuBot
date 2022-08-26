from typing import Sequence

import discord
import json
import random


class SlidesGame:

    def __init__(self, interaction: discord.Interaction, size: int) -> None:
        self.embed = discord.Embed(title='Game', description='Moves: 0', color=discord.Color.og_blurple())
        self.view = SlidePuzzle(interaction.user, self.embed)
        self.view.set_size(size)
    
        self.interaction = interaction
    


class BTile(discord.ui.Button['SlidePuzzle']):
    def __init__(self, label: str, x: int, y: int):
        super().__init__(label=label, row=x)
        self.x = x
        self.y = y

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None

        if interaction.user != self.view.player:
            await interaction.response.send_message('This is not your game', ephemeral=True)
            return


        self.view.add_move()
        self.view.tiless.label, self.label = self.label, self.view.tiless.label
        self.view.tiless = self
        self.view.rearrange_buttons()

        if await self.view.check_win():
            await self.view.win(interaction)
        else:
            await interaction.response.edit_message(view=self.view)


class SlidePuzzle(discord.ui.View):

    children: list[BTile]

    def __init__(self, player: discord.User | discord.Member, embed: discord.Embed):
        super().__init__(timeout=None)
        
        self.player = player
        self.moves = 0

        self._leaderboard_path = 'games/slides/leaderboard.json'
        self.embed = embed

    
    def set_size(self, size: int) -> None:
        items: list[str] = [str(num+1) for num in range((size*size)-1)]
        tiles = [items.pop(random.randint(0, len(items)-1)) for _ in range(len(items))]
        while not self.solvable(tiles):
            random.shuffle(tiles)

        self.size = size
        for x in range(size):
            for y in range(size):
                if not (x == y == size-1):
                    tile = BTile(tiles.pop(0), x, y)
                    self.add_item(tile)
        
        self.tiless = BTile('\u200b', size-1, size-1)
        self.add_item(self.tiless)

    def solvable(self, tiles: Sequence[str]) -> bool:
        counter = 0
        for index, tile1 in enumerate(tiles[:-1]):
            for tile2 in tiles[index: ]:
                if int(tile1) > int(tile2):
                    counter += 1

        return counter % 2 == 0

    def rearrange_buttons(self) -> None:
        for button in self.children:
            if button.label == str((self.size * button.x) + button.y + 1):
                button.style = discord.ButtonStyle.green
            else:
                button.style = discord.ButtonStyle.grey

            if button.y == self.tiless.y and (button.x == self.tiless.x -1 or button.x == self.tiless.x +1):
                button.disabled = False
                
            elif button.x == self.tiless.x and (button.y == self.tiless.y -1 or button.y == self.tiless.y +1):
                button.disabled = False
                
            elif button == self.tiless:
                button.disabled = True
               
            else:
                button.disabled = True

    def add_move(self) -> None:
        self.moves += 1
        self.embed.description = f'Moves: {self.moves}'

    async def check_win(self) -> bool:
        items = tuple(str(num+1) for num in range(self.size*self.size))
        for index, child in enumerate(self.children):
            if items[index] == child.label or child.label == '\u200b':
                continue
            return False
        return True

    async def end_game(self) -> None:
        for child in self.children:
            child.style = discord.ButtonStyle.green
            child.disabled = True

    async def leaderboard(self) -> dict[str, dict[str, dict[str, int]]]:
        with open(self._leaderboard_path) as f:
            l = json.load(f)
        return l

    async def enter_leaderboard(self) -> None:
        leaderboard = await self.leaderboard()
        category = leaderboard[f'{self.size}x{self.size}']
        game = {'user': self.player.id, 'score': self.moves}
        crank = str(len(category.keys())+1)
        copycat = list(category.copy().keys())

        category[crank] = game

        for rank in copycat[:: -1]:
            if category[rank]['score'] > self.moves:
                category[crank] = category[rank]
                category[rank] = game
                crank = rank
                continue
            break
        with open(self._leaderboard_path, 'w') as f:
            json.dump(leaderboard, f, indent=4)

    async def win(self, interaction: discord.Interaction) -> None:
        await self.end_game()
        await interaction.response.edit_message(content='You won!', view=self)
        leaderboard = await self.leaderboard()
        if len(leaderboard) < 50 or leaderboard[f'{self.size}x{self.size}']['50']['score'] < self.moves:
            await self.enter_leaderboard()
            if len(leaderboard) < 10 or leaderboard[f'{self.size}x{self.size}']['10']['score'] < self.moves:
                await interaction.followup.send(f'Congratulations {self.player.mention}! You are now in the leaderboard!\nUse `/game leaderboard [game: slides]` to see it!')