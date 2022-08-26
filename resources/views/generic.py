import discord


class GenericMultiPage(discord.ui.View):

    def __init__(self, embeds: list[discord.Embed]):
        super().__init__()
        self.embeds = embeds
        self._index = 0
        self.response: discord.Message | None = None

    async def on_timeout(self) -> None:
        for btn in self.children:
            btn.disabled = True
        if self.response is not None:
            await self.response.edit(view=self)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value: int):
        if value == 0:
            self.children[0].disabled = True; self.children[1].disabled = True
            self.children[2].disabled = False; self.children[3].disabled = False
        
        elif value == len(self.embeds)-1:
            self.children[0].disabled = False; self.children[1].disabled = False
            self.children[2].disabled = True; self.children[3].disabled = True

        self._index = value

    @property
    def children(self) -> list[discord.ui.Button]:
        return super().children # type: ignore


    async def edit_message(self, interaction: discord.Interaction):
        return await interaction.response.edit_message(embed=self.embeds[self.index], view=self)

    @discord.ui.button(label='<<', disabled=True)
    async def back_btn1(self, interaction: discord.Interaction, _):
        self.index = 0
        await self.edit_message(interaction)

    @discord.ui.button(label='<', disabled=True)
    async def back_btn2(self, interaction: discord.Interaction, _):
        self.index -= 1
        await self.edit_message(interaction)

    @discord.ui.button(label='>')
    async def forward_btn1(self, interaction: discord.Interaction, _):
        self.index += 1
        await self.edit_message(interaction)

    @discord.ui.button(label='>>')
    async def forward_btn2(self, interaction: discord.Interaction, _):
        self.index = len(self.embeds)-1
        await self.edit_message(interaction)