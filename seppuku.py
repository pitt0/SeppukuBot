from discord import app_commands as slash
from dotenv import load_dotenv
from enum import Enum, auto

import asyncio
import datetime
import discord
import os
import pytz
import random

import groups

from models import EmbeddableMessage
from resources import Friendship
from resources import utils


client = discord.Client(intents=discord.Intents.all())
tree = slash.CommandTree(client)

MEMAS_ID = int(os.getenv("MEME_CHANNEL_ID", 0))


async def _handle_reddit(message: EmbeddableMessage) -> None:
    if (not message.is_reddit()):
        return
    
    embed = message.to_embed()
    memas_channel: discord.TextChannel = await client.fetch_channel(MEMAS_ID) # type: ignore[valid-type]
    await message.delete()
    await memas_channel.send(embed=embed)


async def _handle_bananas(message: EmbeddableMessage) -> None:
    user: discord.User

    if (not message.reactable()):
        return

    if (not utils.event(0.25)):
        return
    
    await asyncio.sleep(random.random() * 3)
    await message.channel.send("pass me the banana")

    def check(r: discord.Reaction):
        print("someone reacted")
        return str(r.emoji) == "🍌"

    try:
        _, user = await client.wait_for("reaction_add", timeout=300.0, check=check)
    except asyncio.TimeoutError:
        return
    else:
        utils.add_friendship(user, 1)


# events
@client.event
async def on_ready():
    for group in (groups.Admin(), groups.Movies(), groups.Game(), groups.Spam()):
        tree.add_command(group)

    await tree.sync()

    await client.change_presence(activity=discord.Game(name="Monke"))
    now = datetime.datetime.now(tz=pytz.timezone("Europe/Rome"))
    print(f"[{now:%T}] Bot started")

@client.event
async def on_message(message: discord.Message):
    utils.add_friendship(message.author, round(random.random(), 2))

    if (isinstance(message.channel, discord.DMChannel)):
        return

    _message = EmbeddableMessage(message)
    await _handle_reddit(_message)
    await _handle_bananas(_message)


# slashes
class Action(Enum):
    Add = auto()
    Remove = auto()

class CommandGroup(Enum):
    Game = auto()
    Movies = auto()
    Utils = auto()
    Spam = auto()

@tree.command(name="commands", description="Add or remove a group of commands")
@slash.check(lambda interaction: Friendship.load(str(interaction.user.id)) >= 5)
async def edit_commands(interaction: discord.Interaction, command_group: CommandGroup, action: Action):
    group = tree.get_command(command_group.name.lower(), guild=interaction.guild)
    assert group is not None

    match action:
        case Action.Add:
            try:
                tree.add_command(group, guild=interaction.guild)
            except slash.CommandAlreadyRegistered:
                await interaction.response.send_message(f"{group.name} commands are already loaded.", ephemeral=True)
                return
        case Action.Remove:
            tree.remove_command(group.name, guild=interaction.guild)
    await tree.sync(guild=interaction.guild)
    await interaction.response.send_message(
        embed=discord.Embed(
            title="Success", 
            description=f"{group.name} commands {action.name.removesuffix('e')}ed!", 
            color=discord.Color.og_blurple()
        )
    )

class Monkes(Enum):
    MonkeSam = "https://cdn.discordapp.com/attachments/908827837438496849/908827992908779530/ameriscimmia.jpg"
    BananaScimmia = "https://cdn.discordapp.com/attachments/908827837438496849/908827995542794270/bananascimmia.jpg"
    Joele = "https://cdn.discordapp.com/attachments/908827837438496849/908827999061827604/ciccioscimmia.jpg"
    LastBanana = "https://cdn.discordapp.com/attachments/908827837438496849/908828000718577674/danu.jpg"
    Danu = "https://cdn.discordapp.com/attachments/908827837438496849/908828001595174922/danuscimmia.jpg"
    PuocoScimmia = "https://cdn.discordapp.com/attachments/908827837438496849/908828023653015654/piroscimmia.jpg"
    IdroScimmia = "https://cdn.discordapp.com/attachments/908827837438496849/908828025632735332/idroscimmia.jpg"
    DrScimmia = "https://cdn.discordapp.com/attachments/908827837438496849/908828028329664523/mediscimmia.jpg"
    HARAMBO = "https://cdn.discordapp.com/attachments/908827837438496849/908828062894923806/haramboscimmia.jpg"
    RejectHumanity = "https://cdn.discordapp.com/attachments/908827837438496849/908828080255139850/rejecthumanity.jpg"
    HiroScimmia = "https://cdn.discordapp.com/attachments/908827837438496849/908828114107379722/Hiroscimmia.png"
    FukuScimmia = "https://cdn.discordapp.com/attachments/908827837438496849/908828120717623306/Fukuscimmia.png"
    TecnoScimmia = "https://cdn.discordapp.com/attachments/908827837438496849/908828128217006162/Tecnoscimmia.png"
    TurboScimmia = "https://cdn.discordapp.com/attachments/908827837438496849/908828129903136778/Turboscimmia.png"
    RamboScimmia = "https://cdn.discordapp.com/attachments/908827837438496849/908828134072254545/Ramboscimmia.png"
    SballoScimmia = "https://cdn.discordapp.com/attachments/908827837438496849/908828134382661662/Sballoscimmia.png"


@tree.command(name="monke", description="Sends a monke")
async def send_monke(interaction: discord.Interaction, monke: Monkes = Monkes.IdroScimmia):
    utils.add_friendship(interaction.user, 0.5)

    await interaction.response.send_message(monke.value)

if __name__ == "__main__":
    load_dotenv("./secrets/.env")
    client.run(os.getenv("TOKEN", ""))