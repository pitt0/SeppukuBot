# from typing import Any, Sequence


# def assets(asset: str, *, path: Sequence[str]) -> Any:
#     for dir in path[::-1]:
#         asset = f"{dir}/{asset}"
#     with open(f"assets/{asset}") as f:
#         return f

from resources import Friendship

import discord
import random


def add_friendship(user: discord.User | discord.Member, amount: float) -> None:
    with Friendship() as friendship:
        user_id = str(user.id)
        if (user_id not in friendship):
            friendship[user_id] = 0
        friendship[user_id] += amount

def event(cap: float) -> bool:
    """Returns a bool that represents whether a certain event (which has a cap) happens."""
    return random.random() <= cap
