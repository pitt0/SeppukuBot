from typing import TYPE_CHECKING

import discord

__all__ = (
    'CompView', 
    'ChampView'
    )

class CompButtons(discord.ui.Button['CompView']):

    if TYPE_CHECKING:
        label: str
        view: 'CompView'

    def __init__(self, role: str):
        super().__init__(label=role)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.view.roles[self.label], view=self.view)

class CompView(discord.ui.View):

    def __init__(self, embeds: list[discord.Embed]):
        super().__init__()
        self.roles = {
            'Top': embeds[0],
            'Jng': embeds[1],
            'Mid': embeds[2],
            'ADC': embeds[3],
            'Supp': embeds[4]
            }
        for role in self.roles:
            self.add_item(CompButtons(role))

        self.response: discord.Message | None = None

    @property
    def children(self) -> list[discord.ui.Button]:
        return super().children # type: ignore 

    async def on_timeout(self) -> None:
        children = self.children
        for btn in children:
            btn.disabled = True
        if self.response is not None:
            await self.response.edit(view=self)


class ChampView(discord.ui.View):

    def __init__(self, embeds: list[discord.Embed]):
        super().__init__()
        self.champion = embeds
        self.response: discord.Message | None = None

    @property
    def children(self) -> list[discord.ui.Button]:
        return super().children # type: ignore

    async def on_timeout(self) -> None:
        children: list[discord.ui.Button] = self.children
        for btn in children:
            btn.disabled = True
        if self.response is not None:
            await self.response.edit(view=self)

    @discord.ui.button(label='Lore')
    async def lore(self, interaction: discord.Interaction, _):
        await interaction.response.edit_message(embed=self.champion[0], view=self)

    @discord.ui.button(label='Stats')
    async def statistics(self, interaction: discord.Interaction, _):
        await interaction.response.edit_message(embed=self.champion[1], view=self)
