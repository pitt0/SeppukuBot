import asyncio
import discord
import random

from .resources import *
from .typings import *



class TicTacToeGame:

    def __init__(self, interaction: discord.Interaction, opponent: Opponent):
        self.view = VTicTacToe(interaction.user, opponent)
        self.embed = discord.Embed(
            title = 'Tic Tac Toe',
            description = f'{interaction.user.display_name} vs {opponent.display_name}',
            color = discord.Colour.og_blurple()
        )

        self.interaction = interaction



class FieldButton(discord.ui.Button['VTicTacToe']):

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        super().__init__(label='\u200b', row=y)

    async def change_style(self):
        assert self.view is not None
        match self.view.turn:
            case Turn.X:
                self.style = discord.ButtonStyle.red
            case Turn.O:
                self.style = discord.ButtonStyle.green
            case _:
                self.style = discord.ButtonStyle.grey

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        # Checks
        if interaction.user not in self.view.players.values():
            await interaction.response.send_message('You are not playing', ephemeral=True)
            return
        if interaction.user != self.view.players[self.view.turn]:
            await interaction.response.send_message('Wait for your turn', ephemeral=True)
            return

        await interaction.response.defer()

        # Button
        self.disabled = True
        self.label = self.view.turn.name
        await self.change_style()

        # Game
        self.view.place(self)
        await interaction.response.edit_message()

        # Game Checks
        children = self.view.children
        if self.view.check_win():
            self.view._done()
            self.view.winner = interaction.user # type: ignore[valid-type]
            for child in children:
                child.disabled = True
            return

        if all(btn.disabled for btn in children):
            self.view._done()
            return


class VTicTacToe(discord.ui.View):

    children: list[FieldButton]
    board: Board = Board()
    winner: User | None = None
    turn: Turn = random.choice(tuple(Turn._member_map_.values())) # type: ignore
    
    def __init__(self, player1: User, player2: Opponent):
        super().__init__()
        
        self.players: dict[Turn, Player] = {
            Turn.X: player1,
            Turn.O: player2
            }

        for x in range(3):
            for y in range(3):
                self.add_item(FieldButton(x, y))

        loop = asyncio.get_running_loop()
        self.__done: asyncio.Future[bool] = loop.create_future()

    
    def _done(self):
        assert not self.__done.done()
        self.__done.set_result(True)

    async def wait(self):
        return await self.__done

    def place(self, button: FieldButton) -> None:
        self.board.place(self.turn, button.x, button.y)

    def check_win(self):
        self.board.game_ended()

    def place_AI(self):
        pass