import discord
import os

from utils.fileCogs import FileCog
from discord.ext import commands
from utils.utils import safe_run, tablify
from utils.discord_string import DiscordString


class IngSays(FileCog):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot, 'ingsays')

    @commands.command(name='ingcansay')
    @safe_run
    async def list_ingsays(self, ctx: commands.Context) -> None:
        files = self.list()
        if len(files) == 0:
            await ctx.send("No tags found")
            return

        names = list(map(lambda p: os.path.splitext(p)[0], files))

        ds = DiscordString()
        ds.toggle_pre_block()
        ds.join('\n', tablify(names))
        ds.toggle_pre_block()

        await ctx.send(str(ds))

    @commands.command(name='ingsays')
    @safe_run
    async def ingsays(self, ctx: commands.Context, name: str = None) -> None:
        attachments = ctx.message.attachments

        if len(attachments) > 0:
            for att in attachments:
                await self._save(ctx, name, att)
        else:
            await self._get(ctx, name)

    async def _save(self, ctx: commands.Context, name: str, attachment: discord.Attachment) -> None:
        if name is not None:
            path = self.get_path([f"{name}.mp3"])
        else:
            path = attachment.filename

        await attachment.save(path)
        await ctx.send(f"Saved {attachment.content_type} with tag '{name}'")

    async def _get(self, ctx: commands.Context, name: str) -> None:
        assert name is not None, "No name provided"

        path = self.get_path([f"{name}.mp3"])

        await ctx.send(file=discord.File(path))

    @commands.command(name="ingforgets")
    @safe_run
    async def drop(self, ctx: commands.Context, *names):
        for name in names:
            self.delete(f"{name}.mp3")
            await ctx.send(f"Successfully forgot '{name}'")


def setup(bot):
    bot.add_cog(IngSays(bot))
