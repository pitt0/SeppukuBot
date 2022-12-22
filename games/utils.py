import discord

from resources import add_friendship

async def punish(interaction: discord.Interaction, loss: float):
    add_friendship(interaction.user, loss)
    await interaction.response.send_message(
        "*Stop right there!*\n"
        + "You cannot perform that action in someone else's game."
        + "You lost some friendship.",
        ephemeral=True
    )
