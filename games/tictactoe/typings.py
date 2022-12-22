from typing import Literal

import discord

__all__ = (
    "Position",
    "User",
    "Opponent",
    "Player"
)

Position = Literal[-1, 0, 1]

User = discord.User | discord.Member
Opponent = discord.Member | discord.ClientUser
Player = User | Opponent