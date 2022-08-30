import discord

from models import Movie


class WLView(discord.ui.View):

    children: list[discord.ui.Button]
    d_movies: list[list[Movie]]

    embed: discord.Embed

    def __init__(self, movies: list[Movie], person: str):
        super().__init__()
        self.movies = movies
        self.person = person

        self._divide_movies()

        self.index = 0


    def _divide_movies(self):
        self.d_movies: list[list[Movie]] = [
            [movie for movie in self.movies[i * 15 : (i+1) * 15]] for i in range(len(self.movies)//15)
        ]
        
        if len(self.movies) % 15:
            self.d_movies.append([movie for movie in self.movies[(len(self.movies)//15) * 15 : len(self.movies)]])

    def _generate_embed(self, index: int):
        self.embed = discord.Embed(
            title=f'{self.person} WatchList', 
            description=f'Page {index+1}', 
            color=discord.Color.dark_blue()
            )
        for movie in self.d_movies[index]:
            self.embed.add_field(
                name=movie.title, 
                value=', '.join(movie.genres), 
                inline=True
                )
    
    def _generate_empty_embed(self):
        self.embed = discord.Embed(
            title=f'{self.person} WatchList',
            description='Empty :(',
            color=discord.Color.dark_blue()
        )

    def _update(self, index: int) -> None:
        try:
            self.d_movies[index]
        except IndexError:
            index -= 1

        if index == -1:
            self._generate_empty_embed()
            self._to_remove.options = []
        else:
            self._generate_embed(index)
            self._to_remove.options = [
                discord.SelectOption(
                    label=movie.title, 
                    description=movie.cast[0],
                    value=str(self.movies.index(movie))
                ) for movie in self.d_movies[index]
            ]

        self._to_first.disabled = self.back.disabled = (index == 0)
        self.forward.disabled = self._to_last.disabled = (index == len(self.d_movies) - 1)

    @property
    def index(self) -> int:
        return self.__index

    @index.setter
    def index(self, value: int):
        assert (0 <= value <= len(self.movies) - 1), f'Value set for index: {value}'

        self._update(value)

        self.__index = value

    @discord.ui.button(label='<<')
    async def _to_first(self, interaction: discord.Interaction, _):
        self.index = 0

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='<')
    async def back(self, interaction: discord.Interaction, _):
        self.index -= 1

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='>')
    async def forward(self, interaction: discord.Interaction, _):
        self.index += 1

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.button(label='>>')
    async def _to_last(self, interaction: discord.Interaction, _):
        self.index = len(self.movies) - 1

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.select(placeholder='Remove a Movie', options=[])
    async def _to_remove(self, interaction: discord.Interaction, _):
        assert interaction.data is not None
        index = int(interaction.data['values'][0]) # type: ignore
        self.movies.pop(index)
        self._update(self.index)
        await interaction.response.send_message(embed=self.embed, view=self)