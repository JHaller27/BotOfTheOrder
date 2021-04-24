import discord
from utils.fileCogs import FileCog
from discord.ext import commands


class IngSays(FileCog):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot, 'ingsays')

    @commands.command()
    async def ingsays(self, ctx: commands.Context, name: str) -> None:
        await ctx.send(file=discord.File(self.get_path([f"{name}.mp3"])))


def setup(bot):
    bot.add_cog(IngSays(bot))
