from discord import app_commands as slash

import asyncio
import discord

from resources import Settings

class Spam(slash.Group):

    spamming: bool = False

    @staticmethod
    def set_text(user: discord.User | discord.Member, text: str):
        if (Settings.load("name")):
            text = f"{user.display_name}: {text}"
        return text

    @slash.command(name="start", description="Starts spamming.")
    async def start_spamming(self, interaction: discord.Interaction, text: str) -> None:
        assert isinstance(interaction.channel, discord.abc.Messageable)

        self.spamming = True
        await interaction.response.send_message("Starting spamming...", ephemeral=True)
        text = self.set_text(interaction.user, text)

        while self.spamming:
            await interaction.channel.send(text)
            await asyncio.sleep(0.5)

    @slash.command(name="stop", description="Stops spamming.")
    async def stop_spamming(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Stopping spamming...", ephemeral=True)
        self.spamming = False
