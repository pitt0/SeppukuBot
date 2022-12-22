from enum import Enum

import asyncio
import discord
import math
import random


class Reel(Enum):
    Rolling = "<a:slots:974775919594045482>"

    Banana = "<:slot_banana:974776757263663174>"
    Cherry = "<:slot_cherry:974776749537771550>"
    Diamond = "<:slot_diamond:974776750624084018>"
    Kiwi = "<:slot_kiwi:974776756546449438>"
    Watermelon = "<:slot_watermelon:974776758597480519>"

REEL = [Reel.Watermelon] * 3 + [Reel.Cherry] * 3 + [Reel.Kiwi] * 3 + [Reel.Banana] * 3 + [Reel.Diamond]



class VEndGame(discord.ui.View):

    # def __init__(self) -> None:
    #     # if i don't do this, button.disabled = True won't have any effect
    #     super().__init__()

    @discord.ui.button(label="Again")
    async def again(self, interaction: discord.Interaction, button: discord.ui.Button):
        button.disabled = True
        game = SlotsGame(interaction)

        await interaction.response.edit_message(embed=game.embed, view=self)
        await game.run()


class SlotsGame:

    def __init__(self, interaction: discord.Interaction) -> None:
        self._reels = [Reel.Rolling] * 3
        self.embed = discord.Embed(title="Slot Machine", color=discord.Color.og_blurple())
        self.embed.add_field(name="\u200b", value=self.reels, inline=True)

        self.interaction = interaction

    @property
    def reels(self) -> str:
        return "|".join(f"{self._reels[i].value}" for i in range(3))

    def stop_reel(self, index: int) -> None:
        self._reels[index] = random.choice(REEL)

    def update_fields(self) -> None:
        self.embed.clear_fields()
        self.embed.add_field(name="\u200b", value=self.reels, inline=True)

    async def run(self) -> None:
        message = await self.interaction.original_response()
        for i in range(3):
            to_sleep = math.sqrt(random.random() + 0.1) * 2
            await asyncio.sleep(to_sleep)
            self.stop_reel(i)
            self.update_fields()
            await self.interaction.followup.edit_message(message.id, embed=self.embed)
        await self.done()

    async def done(self) -> None:
        message = await self.interaction.original_response()
        reels = self._reels
        if reels[0] == reels[1] == reels[2]:
            if Reel.Diamond in reels:
                self.embed.title = "JACKPOT!"
                self.embed.description = "Three diamonds! You should ask your crush out!"
                self.embed.color = discord.Color.from_rgb(33, 229, 255)
            else:
                self.embed.title = "You Won!"
                self.embed.description = "Three out of three! How lucky!"
                self.embed.color = discord.Color.from_rgb(87, 252, 5)
        elif reels[0] != reels[1] != reels[2] != reels[0]:
            if Reel.Diamond in reels:
                self.embed.title = "You Won"
                self.embed.description = "There is a diamond, could be worse."
                self.embed.color = discord.Color.from_rgb(50, 191, 252)
            else:
                self.embed.title = "You Lost"
                self.embed.description = "Everyhting's different :c. Try again!"
                self.embed.color = discord.Color.from_rgb(104, 36, 37)
        elif any(reels[i] == reels[i-1] for i in range(3)):
            self.embed.title = "You Won"
            if Reel.Diamond in reels:
                self.embed.description = "There is a diamond and a couple! Good!"
                self.embed.color = discord.Color.from_rgb(0, 200, 180)
            else:
                self.embed.description = "There's a couple! Nice!"
                self.embed.color = discord.Color.from_rgb(45, 206, 93)
        await self.interaction.followup.edit_message(message.id, embed=self.embed, view=VEndGame())