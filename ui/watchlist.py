import discord

from models import Movie


WatchListPage = list[Movie]

class WLView(discord.ui.View):

    children: list[discord.ui.Button]
    pages: list[WatchListPage]

    embed: discord.Embed

    def __init__(self, movies: list[Movie], person: str):
        super().__init__()
        self.movies = movies
        self.person = person

        self.pages = []

        self._divide_movies()

        self.index = 0


    def _divide_movies(self):
        for i in range(len(self.movies)//15):
            page = self.movies[i * 15 : (i + 1) * 15]
            movies = [movie for movie in page]
            self.pages.append(movies)
        
        if len(self.movies) % 15:
            page = self.movies[(len(self.movies)//15) * 15 : len(self.movies)]
            movies = [movie for movie in page]
            self.pages.append(movies)

    def _generate_embed(self):
        self.embed = discord.Embed(
            title=f"{self.person} WatchList", 
            description=f"Page {self.index+1}", 
            color=discord.Color.dark_blue()
        )
        for movie in self.pages[self.index]:
            self.embed.add_field(
                name=movie.title, 
                value=movie.genres, 
                inline=True
            )
    
    def _generate_empty_embed(self):
        self.embed = discord.Embed(
            title=f"{self.person} WatchList",
            description="Empty :(",
            color=discord.Color.dark_blue()
        )

    def _build_to_remove_options(self):
        for movie in self.pages[self.index]:
            self._to_remove.options.append(
                discord.SelectOption(
                    label=movie.title,
                    description=movie.cast,
                    value=str(self.movies.index(movie))
                )
            )

    def _update(self) -> None:

        self._to_remove.options = []
        
        if len(self.pages) == 0:
            self._generate_empty_embed()
        else:
            self._generate_embed()
            self._build_to_remove_options()        

        self._to_first.disabled = self.back.disabled = (self.index == 0)
        self.forward.disabled = self._to_last.disabled = ((self.index == len(self.pages) - 1) or (len(self.pages) == 0)) 

    @property
    def index(self) -> int:
        return self.__index

    @index.setter
    def index(self, value: int):
        assert (0 <= value <= len(self.pages) - 1), f"Value set for index: {value}\nNumber of pages: {len(self.pages)}"

        self.__index = value
        self._update()

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
        self.index = len(self.pages) - 1

        await interaction.response.edit_message(embed=self.embed, view=self)

    @discord.ui.select(placeholder="Remove a Movie", options=[])
    async def _to_remove(self, interaction: discord.Interaction, _):
        assert interaction.data is not None
        index = int(interaction.data["values"][0]) # type: ignore[assignment]
        self.movies.pop(index)
        self._update()
        await interaction.response.send_message(embed=self.embed, view=self)