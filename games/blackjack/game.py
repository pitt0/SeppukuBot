from typing import Literal
import discord
import random

from games.abc import VJoinable, ELobby
from .resources import *
from .typings import *

from resources import GenericMultiPage

class BJLobby:

    lobby: list[Player]

    def __init__(self, interaction: discord.Interaction) -> None:
        self.interaction = interaction

        self.view = VJoinable(interaction.user)
        self.embed = ELobby(interaction.user)

    def __iter__(self):
        return (player for player in self.lobby)

    def __getitem__(self, index: int) -> Player:
        return self.lobby[index]

    def index(self, user: discord.User | discord.Member) -> int:
        return self.lobby.index(user) # type: ignore

    # def remove(self, player: Player) -> None:
    #     return self.lobby.remove(player)

    async def run(self):
        await self.interaction.response.send_message(embed=self.embed, view=self.view)
        await self.view.wait()
        self.lobby = []
        for user in self.view.lobby:
            self.lobby.append(Player(user))

class BJGame:

    __slots__ = (
        'deck',
        'lobby',
        'dealer',
    )

    deck: list[Card]
    lobby: BJLobby
    dealer: Dealer

    def __init__(self, lobby: BJLobby) -> None:
        self.lobby = lobby

    def shuffle_deck(self) -> None:
        self.deck = []
        for _ in range(2):
            for suit in Suits:
                for value in CardValues:
                    self.deck.append(Card(value, suit))

        random.shuffle(self.deck)
    
    def embeds(self, current_player: Player) -> list[discord.Embed]:
        es = []
        es.append(self.dealer.embed)
        for player in self.lobby:
            if player != current_player:
                player.embed.title = player.name
                player.embed.description = f"{player.name}'s score is {player.score}"
            es.append(player.embed)
        return es

    async def update_lobby(self):
        for player in self.lobby:
            embeds = self.embeds(player)
            view = GenericMultiPage(embeds)
            await player.update(embed=embeds[0], view=view)

    def hit(self, player: Player | Dealer, visible: bool = True) -> None:
        card = self.deck.pop(-1)
        card.face = int(visible) # type: ignore
        player.draw(card)

    async def start(self) -> None:
        self.dealer = Dealer()
        self.shuffle_deck()
        for i in range(2):
            for player in self.lobby:
                self.hit(player)
                self.hit(self.dealer, visible=not bool(i))
        await self.update_lobby()

    async def turn_of(self, player: Player):
        view = VBlackJack()
        await player.edit_message(view=view)
        await view.wait()
        if view.result:
            self.hit(player)
            if player.score >= 21:
                player.stay()
        else:
            player.stay()
        await self.update_lobby()

    async def end(self) -> None:
        high_score = 0
        for player in sorted(self.lobby, key=lambda p: p.score, reverse=True):
            if player.score < 20:
                high_score = player.score
                break
        
        while self.dealer.score < high_score:
            self.hit(self.dealer)

        for player in self.lobby:
            if self.dealer.score <= player.score <= 21 or player.score <= 21 < self.dealer.score:
                await player.win(self.dealer)
            else:
                await player.lose(self.dealer)

    async def run(self):
        await self.start()
        while True:
            for player in self.lobby:
                if player.playing:
                    await self.turn_of(player)
            if not any(p.playing for p in self.lobby):
                break
        await self.end()


class VBlackJack(discord.ui.View):

    result: Literal[1, 0]

    def __init__(self) -> None:
        super().__init__()


    @discord.ui.button(label='Hit')
    async def give_card(self, interaction: discord.Interaction, _) -> None:
        await interaction.response.defer()
        self.result = 1
        # await asyncio.sleep(1)
        self.stop()
        # return


    @discord.ui.button(label='Stand')
    async def _stop(self, interaction: discord.Interaction, _) -> None:
        await interaction.response.defer()
        self.result = 0
        # await asyncio.sleep(1)
        self.stop()
        # return