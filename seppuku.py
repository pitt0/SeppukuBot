from dotenv import load_dotenv
from discord import app_commands as slash
from enum import Enum, auto
from typing import Literal

import asyncio
import datetime
import discord
import os
import pytz
import random

import constants as const
import groups

from models import EmbeddableMessage
from resources import database
from resources import utils


client = discord.Client(intents=discord.Intents.all())
tree = slash.CommandTree(client=client)


async def _handle_reddit(message: EmbeddableMessage) -> None:
    if message.is_reddit():
        embed = message.to_embed()
        memas_channel: discord.TextChannel = await client.fetch_channel(const.MEMAS_ID) # type: ignore[valid-type]
        await message.delete()
        await memas_channel.send(embed=embed)

async def _handle_bananas(message: EmbeddableMessage) -> None:
    reaction: discord.RawReactionActionEvent

    if not message.reactable():
        return

    send = random.random()
    if send > 0.25:
        return
    
    await asyncio.sleep(random.random() * 3)
    await message.channel.send('pass me the banana')

    reaction = await client.wait_for('raw_reaction_add')

    if reaction.emoji.name == '🍌':
        friendships = database.friendship()
        if str(message.author.id) not in friendships:
            friendships[str(message.author.id)] = 0

        friendships[str(message.author.id)] += 1
        database.edit_friendship(friendships)



# events
@client.event
async def on_ready():
    for group in (groups.Admin(), groups.Movies(), groups.Game(), groups.Spam()):
        tree.add_command(group)

    await tree.sync()

    await client.change_presence(activity=discord.Game(name='Monke'))
    now = datetime.datetime.now(tz=pytz.timezone('Europe/Rome')).strftime('%H:%M:%S')
    print(f'[{now}] Bot started')

@client.event
async def on_message(message: discord.Message):
    utils.add_friendship(message.author, round(random.random(), 2))

    if isinstance(message.channel, discord.DMChannel):
        return
    _message = EmbeddableMessage(message)
    if _message.is_reddit():
        await _handle_reddit(_message)
    await _handle_bananas(_message)



# slashes
class Action(Enum):
    Add = auto()
    Remove = auto()

@tree.command(name='commands', description='Add or remove a group of commands')
@slash.check(lambda interaction: str(interaction.user.id) in database.friendship() and database.friendship()[str(interaction.user.id)] >= 5)
async def edit_commands(interaction: discord.Interaction, command_group: Literal['Game', 'Movies', 'Utils', 'Spam'], action: Action):
    group = tree.get_command(command_group.lower(), guild=interaction.guild)
    assert group is not None

    match action:
        case Action.Add:
            try:
                tree.add_command(group, guild=interaction.guild)
            except slash.CommandAlreadyRegistered:
                await interaction.response.send_message(f'{group.name} commands are already loaded.', ephemeral=True)
                return
        case Action.Remove:
            tree.remove_command(group.name, guild=interaction.guild)
    await tree.sync(guild=interaction.guild)
    await interaction.response.send_message(embed=discord.Embed(title='Success', description=f'{group.name} commands {action.name.removesuffix("e")}ed!', color=discord.Color.og_blurple()))



if __name__ == '__main__':
    load_dotenv('./secrets/.env')
    client.run(os.getenv('TOKEN')) # type: ignore