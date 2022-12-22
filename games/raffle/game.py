import asyncio
import discord
import random

class RaffleGame:

    participants: list[discord.User | discord.Member]

    def __init__(self, interaction: discord.Interaction, seconds: int):
        self.embed = discord.Embed(
            title="Raffle",
            description="The more the participants, the more the prize.",
            color=discord.Color.orange()
        )
        self.view = ParticipationView(self)

        self.interaction = interaction
        self.participants = []
        self.seconds = seconds

    def add_participant(self, user: discord.User | discord.Member):
        if (user not in self.participants):
            self.participants.append(user)
        else:
            self.participants.remove(user)

        # TODO: Edit embed

    async def run(self):
        await self.interaction.response.send_message(embed=self.embed, view=self.view)
        await asyncio.sleep(self.seconds)
        self.view.participate_button.disabled = True

        message = await self.interaction.original_response()
        await self.interaction.followup.edit_message(message.id, view=self.view)

        winner = random.choice(self.participants)
        embed = discord.Embed(
            title="Winner",
            description=f"{winner.display_name} won the raffle!",
            color=discord.Color.orange()
        )
        await self.interaction.followup.edit_message(message.id, embed=embed)
        


class ParticipationView(discord.ui.View):

    def __init__(self, game: RaffleGame):
        self.game = game

    @discord.ui.button(label="Participate")
    async def participate_button(self, interaction: discord.Interaction, _):
        # TODO: Add a check to check user's credits
        self.game.add_participant(interaction.user)