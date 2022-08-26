# from typing import Any, Sequence


# def assets(asset: str, *, path: Sequence[str]) -> Any:
#     for dir in path[::-1]:
#         asset = f'{dir}/{asset}'
#     with open(f'assets/{asset}') as f:
#         return f

import resources.database as database
import discord


def add_friendship(user: discord.User | discord.Member, amount: float) -> None:
    friendship = database.friendship()
    if str(user.id) not in friendship:
        friendship[str(user.id)] = 0
    friendship[str(user.id)] += amount
    database.edit_friendship(friendship)