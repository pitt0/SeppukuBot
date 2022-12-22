from discord import ButtonStyle

import asyncio
import discord
import random

from .utils import Color
from .utils import Entry, Tiles

from games.utils import punish



class ColorView(discord.ui.View):

    async def chose(self, interaction: discord.Interaction, color: Color):
        view = NumberView(interaction, color)
        await interaction.response.edit_message(embed=view.embed, view=view)
        self.stop()

    @discord.ui.button(label="Reds", style=ButtonStyle.red)
    async def red_button(self, interaction: discord.Interaction, _):
        await self.chose(interaction, "red")

    @discord.ui.button(label="Blacks", style=ButtonStyle.gray)
    async def black_button(self, interaction: discord.Interaction, _):
        await self.chose(interaction, "black")

    @discord.ui.button(label="Green", style=ButtonStyle.green)
    async def green_button(self, interaction: discord.Interaction, _):
        await self.chose(interaction, "green")



class NumberButton(discord.ui.Button["NumberView"]):

    def __init__(self, number: str, row: int):
        super().__init__(label=number, row=row)
        self.number = number

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        if (interaction.user != self.view.user):
            await punish(interaction, -1)
            return
        
        self.view.bet.number = self.number
        self.view.disable_buttons()
        await self.view.spin(interaction)
        await asyncio.sleep(random.random() * 5)
        
        if (not interaction.message): return
    
        await self.view.result(interaction)
        self.view.stop()
        

class NumberView(discord.ui.View):

    children: list[discord.ui.Button]

    def __init__(self, interaction: discord.Interaction, color: Color):
        super().__init__()
        self.nums = Tiles.load_color(color)
        self.bet = Entry("", color)
        self.user = interaction.user

        for i in range(18):
            self.add_item(NumberButton(self.nums[i], i//4))

        self.embed = discord.Embed(
            title="Roulette",
            description="Here's your choice",
            color=discord.Color.og_blurple()
        ).set_image(url="https://cdn.discordapp.com/attachments/849283906036432937/1012684082062307440/roulette.png")

    @discord.ui.button(label="Skip", row=5)
    async def skip_button(self, interaction: discord.Interaction, _):
        if (interaction.user != self.user):
            await punish(interaction, -1)
            return

        self.disable_buttons()
        await self.spin(interaction)
        await asyncio.sleep(random.random() * 5)
        
        if (not interaction.message): return
    
        await self.result(interaction)
        self.stop()

    def disable_buttons(self):
        for child in self.children:
            child.disabled = True

    async def spin(self, interaction: discord.Interaction):
        self.disable_buttons()
        self.embed.set_image(url="https://imgur.com/rzNGNl4")
        await interaction.response.edit_message(embed=self.embed, view=self)

    def roll(self):
        return Entry.random()

    async def result(self, interaction: discord.Interaction) -> None:
        self.embed.set_image(url="https://cdn.discordapp.com/attachments/849283906036432937/1012684082062307440/roulette.png")
        result = self.roll()
        if (self.bet.number == ""):
            self.bet.number = result.number
        if (result == self.bet):
            self.embed.title = "You Won!"
        else:
            self.embed.title = "You Lost!"
        self.embed.description = f"{result} went out!"
        await interaction.followup.edit_message(interaction.message.id, embed=self.embed, view=self) # type: ignore


class RouletteGame:

    def __init__(self) -> None:
        embed = discord.Embed(
            title="Roulette",
            description="Here's your choice",
            color=discord.Color.og_blurple()
        )
        embed.set_image(url="attachment://roulette.png")
        self.embed = embed        

        self.view = ColorView()
