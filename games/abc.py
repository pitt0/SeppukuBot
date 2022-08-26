import discord


class Game:
    embed: discord.Embed
    view: discord.ui.View


class ELobby(discord.Embed):

    def __init__(self, author: discord.User | discord.Member) -> None:
        super().__init__()
        self.title = 'Lobby'
        self.lobby = [author]
        self.add_field(name=f'Player {1}', value=author.display_name, inline=False)

    def add_user(self, user: discord.User | discord.Member) -> None:
        self.lobby.append(user)
        self.add_field(name=f'Player {len(self.lobby)}', value=user.display_name, inline=False)

    def remove_user(self, user: discord.User | discord.Member) -> None:
        index = self.lobby.index(user)
        self.lobby.remove(user)
        self.remove_field(index)

class VJoinable(discord.ui.View):

    def __init__(self, author: discord.User | discord.Member) -> None:
        super().__init__()
        self.lobby = [author]
        self.embed = ELobby(author)

    @discord.ui.button(label='Join')
    async def join_btn(self, interaction: discord.Interaction, _) -> None:
        if interaction.user in self.lobby:
            await interaction.response.send_message('You are already in the lobby.', ephemeral=True)
            return

        self.lobby.append(interaction.user)
        self.embed.add_user(interaction.user)

        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label='Leave')
    async def leave_btn(self, interaction: discord.Interaction, _) -> None:
        if interaction.user not in self.lobby:
            await interaction.response.send_message('You are not in the lobby.', ephemeral=True)
            return

        self.lobby.remove(interaction.user)
        self.embed.remove_user(interaction.user)

        await interaction.response.edit_message(embed=self.embed)

    @discord.ui.button(label='Ready')
    async def ready_btn(self, interaction: discord.Interaction, _) -> None:
        if interaction.user not in self.lobby:
            await interaction.response.send_message('You are not in the lobby.', ephemeral=True)
            return

        await interaction.message.delete() # type: ignore
        self.stop()