from praw.models import Submission

import discord

from resources.reddit import reddit
import resources.database as database



class EmbeddableMessage(discord.Message):

    def __init__(self, original_message: discord.Message):
        self.message = original_message

    @property
    def channel(self):
        return self.message.channel

    def reactable(self) -> bool:
        return (
            self.message.guild is not None and
            database.Settings.load("banana") and
            any(trigger in self.message.content.casefold() for trigger in database.Triggers.load())
        )

    def is_reddit(self) -> bool:
        return self.message.content.startswith("http") and "reddit.com" in self.message.content

    def to_embed(self) -> discord.Embed:
        content = self.message.content
        author = self.message.author

        submission: Submission = reddit.submission(url=content)
        
        embed = discord.Embed(
            title=submission.title,
            url=f"https://reddit.com/{submission.permalink}",
            color=discord.Color.og_blurple(),
            description=f"by u/{submission.author} in r/{submission.subreddit}"
        )
        embed.set_author(name=author.display_name, icon_url=author.avatar.url if author.avatar is not None else None)
        embed.set_image(url=submission.url if not submission.is_self else "http://localhost:8080")

        return embed

    async def delete(self) -> None:
        await self.message.delete()