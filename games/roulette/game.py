from enum import Enum, auto
from typing import TYPE_CHECKING

import asyncio
import discord
import random

from .abc import RouletteView


ALL = [32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
REDS = (32, 19, 21, 25, 34, 27, 36, 30, 23, 5, 16, 1, 14, 9, 18, 7, 12, 3)
BLACKS = (15, 4, 2, 17, 6, 13, 11, 8, 10, 24, 33, 20, 31, 22, 29, 28, 35, 26)


class Choice(Enum):
    Number = auto()
    Color = auto()
    Dozens = auto()

def button_type(i: int):
    if i < 16:
        return NumberButton(i+21, i//5)
    return EmptyButton(i//5)


class RouletteGame:

    if TYPE_CHECKING:
        view: RouletteView

    def __init__(self, interaction: discord.Interaction, game: Choice) -> None:
        match game:
            case Choice.Number:
                view = VNumberRoulette(interaction.user)
            case Choice.Color:
                view = VColorRoulette(interaction.user)
            case Choice.Dozens:
                view = VDozenRoulette(interaction.user)

        self.view = view
        embed = discord.Embed(
            title='Roulette',
            description="Here's your choice",
            color=discord.Color.og_blurple()
        )
        embed.set_image(url='attachment://roulette.png')
        self.embed = embed        


class EmptyButton(discord.ui.Button):

    def __init__(self, row: int):
        super().__init__(label='\u200b', disabled=True, row=row)

class NumberButton(discord.ui.Button['VNumberRoulette']):
    
    def __init__(self, num: int, row: int):
        if num in REDS:
            style = discord.ButtonStyle.red
        elif num in BLACKS:
            style = discord.ButtonStyle.grey
        else:
            style = discord.ButtonStyle.green
        super().__init__(label=str(num), style=style, row=row)
        self.value = num

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        if interaction.user != self.view.player:
            await interaction.response.send_message('This is not your game. Use `/game roulette <choice>` to create your game.', ephemeral=True)
            return

        self.view.bet = self.value
        self.view.disable_buttons()
        await self.view.spin(interaction)
        await asyncio.sleep(random.random() * 5)
        
        if not interaction.message: return
    
        await self.view.result(interaction)
        self.view.stop()

class VNumberRoulette(RouletteView):

    __index = 0
    bet: int
    first20: list[NumberButton] = [NumberButton(i+1, i//5) for i in range(20)]
    last20: list[NumberButton | EmptyButton] = [button_type(i) for i in range(20)]

    def __init__(self, player: discord.User | discord.Member) -> None:
        super().__init__(player)

        for btn in self.first20:
            self.add_item(btn)

    @property
    def index(self):
        return self.__index

    @index.setter
    def index(self, value: int):
        
        for child in self.children:
            if isinstance(child, (NumberButton, EmptyButton)):
                self.remove_item(child)

        if value == 0:
            self.forward.disabled = False
            self.back.disabled = True
            for btn in self.first20:
                self.add_item(btn)
        
        elif value == 1:
            self.forward.disabled = True
            self.back.disabled = False
            for btn in self.last20:
                self.add_item(btn)

        self.__index = value

    def roll(self) -> int:
        return random.randint(0, 37)

    @discord.ui.button(label='<', disabled=True, row=4)
    async def back(self, interaction: discord.Interaction, _) -> None:
        self.index = 0
        await interaction.response.edit_message(view=self)

    @discord.ui.button(label='>', disabled=False, row=4)
    async def forward(self, interaction: discord.Interaction, _) -> None:
        self.index = 1
        await interaction.response.edit_message(view=self)



class Color(Enum):
    Red = auto()
    Black = auto()



class VColorRoulette(RouletteView):

    bet: Color

    @discord.ui.button(label='Red')
    async def red(self, interaction: discord.Interaction, _) -> None:
        self.bet = Color.Red
        await self.spin(interaction)
        await asyncio.sleep(random.random() * 5)
        await self.result(interaction)
        self.stop()

    @discord.ui.button(label='Black')
    async def black(self, interaction: discord.Interaction, _) -> None:
        self.bet = Color.Black
        await self.spin(interaction)
        await asyncio.sleep(random.random() * 5)
        await self.result(interaction)
        self.stop()

    def roll(self) -> Color:
        return random.choice(list(Color.__members__.values()))



class VDozenRoulette(RouletteView):

    bet: list[int]

    async def play(self, interaction: discord.Interaction) -> None:
        await self.spin(interaction)
        await asyncio.sleep(random.random() * 5)
        await self.result(interaction)

    @discord.ui.button(label='1st Dozen')
    async def first(self, interaction: discord.Interaction, _) -> None:
        self.bet = ALL[: 12]
        await self.play(interaction)
        self.stop()

    @discord.ui.button(label='2nd Dozen')
    async def second(self, interaction: discord.Interaction, _) -> None:
        self.bet = ALL[12: 24]
        await self.play(interaction)
        self.stop()

    @discord.ui.button(label='3rd Dozen')
    async def third(self, interaction: discord.Interaction, _) -> None:
        self.bet = ALL[24: ]
        await self.play(interaction)
        self.stop()

    def roll(self) -> int:
        return random.randint(0, 37)

