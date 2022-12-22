import discord
import random

from games.abc import VJoinable, ELobby
from .resources import *

from ui import MenuView


class BJLobby(list[Player]):

    def __init__(self, interaction: discord.Interaction) -> None:
        super().__init__()
        self.interaction = interaction

    async def run(self):
        view = VJoinable(self.interaction.user)
        await self.interaction.response.send_message(embed=ELobby(self.interaction.user), view=view)
        await view.wait()
        
        for user in view.lobby:
            self.append(Player(user))

class BJGame:

    __slots__ = (
        "deck",
        "lobby",
        "dealer",
    )

    deck: list[Card]
    lobby: BJLobby
    dealer: Dealer

    def __init__(self, interaction: discord.Interaction) -> None:
        self.lobby = BJLobby(interaction)

    def shuffle_deck(self) -> None:
        self.deck = []
        
        for suit in Suits:
            for value in CardValues:
                self.deck.append(Card(value, suit))

        self.deck *= 2 # There are two decks of cards
        random.shuffle(self.deck)
    
    def embeds(self, current: Player) -> list[discord.Embed]:
        es = []
        es.append(self.dealer.embed)
        for player in self.lobby:
            es.append(player.embed(player == current))
        return es

    async def update_lobby(self):
        for player in self.lobby:
            embeds = self.embeds(player)
            view = MenuView(embeds)
            await player.update(embed=embeds[0], view=view)

    def hit(self, player: Player | Dealer, visible: bool = True) -> None:
        card = self.deck.pop(-1)
        card.visible = visible
        player.draw(card)

    async def create_lobby(self) -> None:
        await self.lobby.run()

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
        clicked = not await view.wait()
        if (clicked and view.card):
            self.hit(player)
            if (player.score >= 21):
                player.stay()
        else:
            player.stay()
        await self.update_lobby()

    async def end(self) -> None:
        high_score = 0
        for player in sorted(self.lobby, key=lambda p: p.score, reverse=True):
            if (player.score < 20):
                high_score = player.score
                break
        
        while (self.dealer.score < high_score):
            self.hit(self.dealer)

        for player in self.lobby:
            if (self.dealer.score <= player.score <= 21 or player.score <= 21 < self.dealer.score):
                await player.win(self.dealer)
            else:
                await player.lose(self.dealer)

    async def run(self):
        await self.start()
        while (True):
            for player in self.lobby:
                if (player.playing):
                    await self.turn_of(player)
            if (not any(p.playing for p in self.lobby)):
                break
        await self.end()


class VBlackJack(discord.ui.View):

    card: bool


    @discord.ui.button(label="Hit")
    async def give_card(self, interaction: discord.Interaction, _) -> None:
        await interaction.response.defer()
        self.card = True
        # await asyncio.sleep(1)
        self.stop()
        # return


    @discord.ui.button(label="Stand")
    async def _stop(self, interaction: discord.Interaction, _) -> None:
        await interaction.response.defer()
        self.card = False
        # await asyncio.sleep(1)
        self.stop()
        # return