from enum import Enum, auto
from typing import Literal

import asyncio
import discord.app_commands as slash
import discord

from resources import database



class Settings(Enum):
    Banana = auto()
    Name = auto()
    Unban = auto()
    ReInvite = auto()
    Reddit = auto()

class Admin(slash.Group):

    @slash.command(name='seppuku', description='Bans a member.')
    async def ban(self, interaction: discord.Interaction, who: discord.Member | None = None, unban: bool = False) -> None:
        if who is None:
            who = interaction.user # type: ignore

        await who.ban() # type: ignore
        await interaction.response.send_message(f'{who} has been banned.')
        if unban:
            await asyncio.sleep(60)
            await who.unban() # type: ignore

    @slash.command(name='kick', description='Kicks a member.')
    async def kick(self, interaction: discord.Interaction, who: discord.Member) -> None:
        await who.kick()
        await interaction.response.send_message(f'{who} has been kicked.')

    @slash.command(name='mute', description='Mutes a member.')
    async def mute(self, interaction: discord.Interaction, who: discord.Member) -> None:
        await who.edit(mute=True)
        await interaction.response.send_message(f'{who} has been muted.', ephemeral=True)
    
    @slash.command(name='deafen', description='Deafens a member.')
    async def deafen(self, interaction: discord.Interaction, who: discord.Member) -> None:
        await who.edit(deafen=True)
        await interaction.response.send_message(f'{who} has been deafened.', ephemeral=True)

    @slash.command(name='nick', description="Changes someone's nick.")
    async def change_nickname(self, interaction: discord.Interaction, who: discord.Member | None = None, nick: str | None = None) -> None:
        if who is None:
            who = interaction.user # type: ignore
        try:
            await who.edit(nick=nick or who.name) # type: ignore
            await interaction.response.send_message(f'Nickname changed.', ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message(f'Changing nickname for {who.display_name} failed.') # type: ignore
        
    @slash.command(name='settings', description='Changes some of the settings of the bot')
    @slash.describe(setting='The setting you want to change', value="The setting's new value")
    async def edit_settings(self, interaction: discord.Interaction, setting: Settings, value: Literal['On', 'Off']):
        settings = database.settings()
        settings[setting.name.lower()] = (value=='On')
        database.edit_settings(settings)

        await interaction.response.send_message(embed=discord.Embed(title='Success', description='Settings successfully edited', color=discord.Colour.og_blurple()))