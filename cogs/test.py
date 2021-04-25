from discord.ext import commands
from utils.safe_run import safe_run


class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.command()
    async def foo(self, ctx: commands.Context) -> None:
        # print(str(ctx))
        await ctx.send('bar')

    @commands.command()
    async def toint(self, ctx: commands.Context, *args) -> None:
        await safe_run(self._do, ctx, *args)

    async def _do(self, ctx: commands.Context, *args):
        s = ""
        for arg in args:
            s += f"{int(arg)}"
        await ctx.send(s)


def setup(bot):
    bot.add_cog(Test(bot))
