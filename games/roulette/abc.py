from typing import Any
import discord

class RouletteView(discord.ui.View):

    bet: Any
    children: list[discord.ui.Button]

    def __init__(self, player: discord.User | discord.Member):
        self.player = player
        self.embed = discord.Embed(
            title='Roulette',
            description="Here's your choice",
            color=discord.Color.og_blurple()
        ).set_image(url='https://cdn.discordapp.com/attachments/849283906036432937/1012684082062307440/roulette.png')
        

    def disable_buttons(self) -> None:
        for child in self.children:
            child.disabled = True

    async def spin(self, interaction: discord.Interaction):
        self.disable_buttons()
        self.embed.set_image(url='https://imgur.com/rzNGNl4')
        await interaction.response.edit_message(embed=self.embed, view=self)

    def roll(self) -> Any:
        ...

    async def result(self, interaction: discord.Interaction) -> None:
        self.embed.set_image(url='https://cdn.discordapp.com/attachments/849283906036432937/1012684082062307440/roulette.png')
        result = self.roll()
        if result == self.bet or result in self.bet:
            self.embed.title = 'You Won!'
        else:
            self.embed.title = 'You Lost!'
        self.embed.description = f'{result} went out!'
        await interaction.followup.edit_message(interaction.message.id, attachments=[file], embed=self.embed, view=self) # type: ignore