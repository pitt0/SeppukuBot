import discord


class MenuView(discord.ui.View):

    children: list[discord.ui.Button]
    embed: discord.Embed

    def __init__(self, embeds: list[discord.Embed]):
        super().__init__()
        self.embeds = embeds

        self.index = 0

    @property
    def index(self) -> int:
        return self.__index

    @index.setter
    def index(self, value: int):
        assert (0 <= value <= len(self.embeds) - 1), f"Value set for index: {value}"

        self.embed = self.embeds[value]

        self._to_first.disabled = self.back.disabled = (value == 0)
        self.forward.disabled = self._to_last.disabled = (value == len(self.embeds) - 1)

        self.__index = value

    @discord.ui.button(label="<<")
    async def _to_first(self, interaction: discord.Interaction, _):
        self.index = 0

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label="<")
    async def back(self, interaction: discord.Interaction, _):
        self.index -= 1

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label=">")
    async def forward(self, interaction: discord.Interaction, _):
        self.index += 1

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label=">>")
    async def _to_last(self, interaction: discord.Interaction, _):
        self.index = len(self.embeds) - 1

        await interaction.response.edit_message(embed=self.embed, view=self)
