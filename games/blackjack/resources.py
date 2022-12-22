from dataclasses import dataclass
from enum import Enum

import discord


__all__ = ("CardValues", "Suits", "Card", "Player", "Dealer")


class CardValues(Enum):
    Ace = 0
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13

class Suits(Enum):
    Diamon = "♦️"
    Clubs = "♣️"
    Hearts = "♥️"
    Spades = "♠️"


@dataclass
class Card:
    value: CardValues
    suit: Suits
    visible: bool = True # whether it is faced up or down

    def __repr__(self):
        if (not self.visible):
            return "🃏"
        if (self.value in (CardValues.Ace, CardValues.Jack, CardValues.Queen, CardValues.King)):
            return f"{self.value.name}{self.suit.value}"
        return f"{self.value.value}{self.suit.value}"

    def __str__(self):
        return self.__repr__()

    @property
    def true(self) -> str:
        _f = self.visible
        self.visible = True
        name = self.__repr__()
        self.visible = _f
        return name

    @property
    def score(self) -> int:
        return self.value.value if self.value.value <= 10 else 10


class CardHandler:

    hand: list[Card]

    @property
    def score(self) -> int:
        s = 0
        for card in self.hand:
            s += card.value.value
        return s
    
    def draw(self, card: Card):
        if (card.value is CardValues.Ace):
            if (self.score + 11 > 21):
                card.value.value = 1
            else:
                card.value.value = 11
        self.hand.append(card)

class Dealer(CardHandler):

    def __init__(self) -> None:
        self.hand = []
        self.name = "Dealer"

    @property
    def embed(self) -> discord.Embed:
        e = discord.Embed(
            title=self.name,
            # description=f"Dealer"s visible score is {self.score}",
            color=discord.Color.og_blurple()
        )
        e.add_field(name="Hand", value="\n".join(str(card) for card in self.hand))
        return e

class Player(CardHandler):

    message: discord.Message

    playing: bool

    def __init__(self, user: discord.User | discord.Member) -> None:
        self.hand = []
        self.user = user
        self.playing = True

    def __eq__(self, __o: object) -> bool:
        return (isinstance(__o, Player) and __o.user.id == self.user.id) or (isinstance(__o, (discord.User, discord.Member)) and __o.id == self.user.id)
       

    @property
    def name(self) -> str:
        return self.user.display_name

    def embed(self, current: bool = False) -> discord.Embed:
        return discord.Embed(
            title="You" if current else self.name,
            description=f"Your score is {self.score}" if current else f"{self.name} score is {self.score}",
            color=discord.Color.og_blurple()
        ).add_field(name="Hand", value="\n".join(str(card) for card in self.hand))
            
    async def send(self, embed: discord.Embed, view: discord.ui.View | None = None) -> discord.Message:
        return await self.user.send(embed=embed, view=view) # type: ignore[valid-type]

    async def edit_message(self, embed: discord.Embed | None = None, view: discord.ui.View = ...) -> None:
        try:
            await self.message.edit(embed=(embed or self.embed()), view=view)
        except discord.NotFound:
            self.message = await self.send(embed=(embed or self.embed()), view=view)

    async def update(self, embed: discord.Embed, view: discord.ui.View) -> discord.Message:
        try:
            await self.edit_message(embed, view)
        except AttributeError:
            self.message = await self.send(embed, view)
        return self.message

    def stay(self) -> None:
        self.playing = False
        for card in self.hand:
            card.visible = True

    async def win(self, dealer: Dealer) -> None:
        e = discord.Embed(
            title="You Won!", 
            # description=f"You won 100 credits",
            color=discord.Color.og_blurple()
        )
        e.add_field(name=f"Your score", value=f"{self.score} points", inline=True)
        e.add_field(name="Dealer's score", value=f"{dealer.score} points", inline=True)
        await self.send(embed=e)

    async def lose(self, dealer: Dealer) -> None:
        e = discord.Embed(
            title="You Lost",
            # description="You lost 50 credits",
            color=discord.Color.dark_red()
        )
        e.add_field(name="Your score", value=f"{self.score} points", inline=True)
        e.add_field(name="Dealer's score", value=f"{dealer.score} points", inline=True)
        await self.send(embed=e)
