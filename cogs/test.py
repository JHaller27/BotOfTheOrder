from discord.ext import commands
from discord import File


class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.command()
    async def foo(self, ctx: commands.Context) -> None:
        # print(str(ctx))
        await ctx.send('bar')


def setup(bot):
    bot.add_cog(Test(bot))
