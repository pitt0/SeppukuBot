# class BTile(discord.ui.Button['SlidePuzzle']):
#     def __init__(self, label: str, x: int, y: int):
#         super().__init__(label=label, row=x)
#         self.x = x
#         self.y = y

#     async def callback(self, interaction: discord.Interaction) -> None:
#         assert self.view is not None

#         if interaction.user != self.view.player:
#             await interaction.response.send_message('This is not your game', ephemeral=True)
#             return
        
#         if self.view.first is None:
#             self.view.first = self
#             self.style = discord.ButtonStyle.green
#             self.view.disable_non_near(self)
            

#         elif self.view.first == self:
#             self.view.first = None
#             self.style = discord.ButtonStyle.grey
#             self.view.enable_all()
            
#         else:
#             first = self.view.first
#             first.label, self.label = self.label, first.label
#             first.style = discord.ButtonStyle.grey
#             self.view.enable_all()
#             self.view.first = None

#         if await self.view.check_win():
#             for child in self.view.children:
#                 child.style = discord.ButtonStyle.green
#                 child.disabled = True
#             await interaction.response.edit_message(content='You won!', view=self.view)
#         else:
#             await interaction.response.edit_message(view=self.view)

        

        

# class SlidePuzzle(discord.ui.View):
#     def __init__(self, player: discord.User | discord.Member, size: int):
#         super().__init__(timeout=None)
#         items: list[str] = [str(num+1) for num in range(size*size)]
        
#         self.size = size
#         self.first: BTile | None = None
#         self.player = player

#         for x in range(size):
#             for y in range(size):
#                 tile = BTile(items.pop(random.randint(0, len(items)-1)), x, y)
#                 self.add_item(tile)


#     @property
#     def children(self) -> list[BTile]:
#         return super().children # type: ignore

#     def disable_non_near(self, tile: BTile) -> None:
#         for button in self.children:
#             if button.y == tile.y and (button.x == tile.x -1 or button.x == tile.x +1):
#                 button.disabled = False
                
#             elif button.x == tile.x and (button.y == tile.y -1 or button.y == tile.y +1):
#                 button.disabled = False
                
#             elif button == tile:
#                 button.disabled = False
               
#             else:
#                 button.disabled = True

#     def enable_all(self) -> None:
#         for button in self.children:
#             button.disabled = False

#     async def check_win(self) -> bool:
#         items = tuple(str(num+1) for num in range(self.size*self.size))
#         for index, child in enumerate(self.children):
#             if items[index] == child.label:
#                 continue
#             return False
#         return True
