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

    @staticmethod
    def _unify_keep_drop(keep: bool, highest: bool, count: int, total: int) -> int:
        """
        Keep-highest = drop-lowest, and keep-lowest = drop-highest
        Thus, we only need 2 possibilities: keep-highest and drop-highest
        Convert keep/drop highest/lowest # into single signed-int where
        +# = keep highest #
        0 = ignore
        -# = drop highest #
        """
        assert total > count

        if not highest:
            # kl/dl
            count = total - count
            # kl
            if keep:
                return -count

        # dh
        elif not keep:
            return -count

        # kh/dl
        return count

    @staticmethod
    def _roll(x: int, y: int, ):
        pass


def setup(bot):
    bot.add_cog(DiceCog(bot))


if __name__ == "__main__":
    data_rows = [
        ((True, True, 2, 5), 2),
        ((True, False, 2, 5), -3),
        ((False, True, 2, 5), -2),
        ((False, False, 2, 5), 3),
    ]

    for args, expected in data_rows:
        actual = DiceCog._unify_keep_drop(*args)
        if actual != expected:
            print(f"Expected {expected}, got {actual}")
