from discord.ext import commands
from utils.safe_run import safe_run


class Test(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.command()
    async def foo(self, ctx: commands.Context) -> None:
        await ctx.send('bar')

    @commands.command(name="toint")
    @safe_run
    async def convert_to_int(self, ctx: commands.Context, val: str, base: str = None):
        ival = int(val) if base is None else int(val, int(base))
        await ctx.send(str(ival))


def setup(bot):
    bot.add_cog(Test(bot))
