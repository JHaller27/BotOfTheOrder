from random import randint
from discord.ext import commands
import re


class DiceCog(commands.Cog):
    DICE_REGEX = re.compile(r'(?P<num>\d+)d(?P<size>\d+)(?P<kd>[kd][hl]\d+)(?P<mod>[+\-]\d+)?(?P<explode>e)?')

    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.command()
    async def roll(self, ctx: commands.Context, num: str, size: str) -> None:
        num = int(num)
        size = int(size)
        rolls = [randint(1, size) for _ in range(num)]

        await ctx.send(f'{rolls}\n{sum(rolls)}')

    @commands.command()
    async def r(self, ctx: commands.Context, roll_str: str):
        pass


def setup(bot):
    bot.add_cog(DiceCog(bot))
