from enum import Enum, auto
from typing import Literal

import asyncio
import discord.app_commands as slash
import discord

from resources import Settings as SettingsDB



class Settings(Enum):
    Banana = auto()
    Name = auto()
    Unban = auto()
    ReInvite = auto()
    Reddit = auto()

class Admin(slash.Group, guild_only=True):

    @slash.command(name="seppuku", description="Bans a member.")
    async def ban(self, interaction: discord.Interaction, who: discord.Member | None = None, unban: bool = False) -> None:
        assert isinstance(interaction.user, discord.Member)
        
        user = who or interaction.user
        await user.ban()
        await interaction.response.send_message(f"{who} has been banned.")

        if (unban or SettingsDB.load("unban")):
            await asyncio.sleep(60)
            await user.unban()

    @slash.command(name="kick", description="Kicks a member.")
    async def kick(self, interaction: discord.Interaction, who: discord.Member) -> None:
        await who.kick()
        await interaction.response.send_message(f"{who} has been kicked.")

    @slash.command(name="mute", description="Mutes a member.")
    async def mute(self, interaction: discord.Interaction, who: discord.Member) -> None:
        await who.edit(mute=True)
        await interaction.response.send_message(f"{who} has been muted.", ephemeral=True)
    
    @slash.command(name="deafen", description="Deafens a member.")
    async def deafen(self, interaction: discord.Interaction, who: discord.Member) -> None:
        await who.edit(deafen=True)
        await interaction.response.send_message(f"{who} has been deafened.", ephemeral=True)

    @slash.command(name="nick", description="Changes someone's nick.")
    async def change_nickname(self, interaction: discord.Interaction, who: discord.Member | None = None, nick: str = "") -> None:
        assert isinstance(interaction.user, discord.Member)

        user = who or interaction.user
        try:
            await user.edit(nick=nick or user.name)
        except discord.Forbidden:
            await interaction.response.send_message(f"Changing nickname for {user.display_name} failed.")
        else:
            await interaction.response.send_message(f"Nickname changed.", ephemeral=True)
        
    @slash.command(name="settings", description="Changes some of the settings of the bot")
    @slash.describe(setting="The setting you want to change", value="The setting's new value")
    async def edit_settings(self, interaction: discord.Interaction, setting: Settings, value: Literal["On", "Off"]):
        with SettingsDB() as settings:
            # TODO: Change settings to be split between servers
            settings[setting.name.lower()] = (value=="On")

        await interaction.response.send_message(embed=discord.Embed(
            title="Success",
            description="Settings successfully edited",
            color=discord.Colour.og_blurple()
        ))