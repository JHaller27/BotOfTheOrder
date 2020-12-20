from random import randint
from discord.ext import commands


class Dice(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.command()
    async def roll(self, ctx: commands.Context, num: str, size: str) -> None:
        num = int(num)
        size = int(size)
        rolls = [randint(1, size) for _ in range(num)]

        await ctx.send(f'{rolls}\n{sum(rolls)}')

    @commands.command()
    async def r(self, *args, **kwargs):
        return await self.roll(*args, **kwargs)


def setup(bot):
    bot.add_cog(Dice(bot))
