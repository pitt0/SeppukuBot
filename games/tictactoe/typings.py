from typing import Literal, TypeAlias

import discord

__all__ = (
    'Position',
    'User',
    'Opponent',
    'Player'
)

Position: TypeAlias = Literal[-1, 0, 1]

User: TypeAlias = discord.User | discord.Member
Opponent: TypeAlias = discord.Member | discord.ClientUser
Player: TypeAlias = User | Opponent