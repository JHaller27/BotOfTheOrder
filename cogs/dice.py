from utils.discord_string import DiscordString
from random import randint
from discord.ext import commands
import re


class DiceCog(commands.Cog):
    DICE_REGEX = re.compile(r'(?P<num>\d+)d(?P<size>\d+)(?P<kd>[kd][hl]\d+)?(?P<explode>e)?(?P<mod>[+\-]\d+)?')

    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.command()
    async def roll(self, ctx: commands.Context, roll_str: str):
        if m := DiceCog.DICE_REGEX.search(roll_str):
            x = int(m['num'])
            y = int(m['size'])
            mod = 0
            drop = 0
            explode = m['explode'] is not None

            if kd := m['kd']:
                drop = DiceCog._unify_keep_drop(kd[0] == 'k', kd[1] == 'h', int(kd[2:]), x)

            if m := m['mod']:
                mod = int(m)

            result, ds = DiceCog._roll(x, y, drop, mod, explode)

            await ctx.send(str(ds))

    @staticmethod
    def _unify_keep_drop(keep: bool, highest: bool, count: int, total: int) -> int:
        """
        Keep-highest = drop-lowest, and keep-lowest = drop-highest
        Thus, we only need 2 possibilities: keep-highest (-) and keep-lowest (+)
        Convert keep/drop highest/lowest # into single signed-int
        """
        assert total > count

        # dh/dl
        if not keep:
            count = total - count

            # dl
            if not highest:
                return -count

        # kh
        elif highest:
            return -count

        # kl/dh
        return count

    @staticmethod
    def _roll(x: int, y: int, drop: int, mod: int, explode: bool) -> (int, DiscordString):
        ds = DiscordString()
        ds.bold('Dice').add(': ')

        rolls = sorted([randint(1, y) for _ in range(x)])
        dropped = []

        if drop < 0:
            rolls, dropped = rolls[drop:], rolls[:drop]
        elif drop > 0:
            rolls, dropped = rolls[:drop], rolls[drop:]

        def _add_roll(roll: int, first):
            if not first:
                ds.add(', ')
            if roll == y:
                ds.bold(str(roll))
                if explode:
                    ds.emoji('boom')
            elif roll == 1:
                ds.bold(str(roll))
            else:
                ds.add(str(roll))

        # Prime explode count
        explode_count = sum([1 for r in rolls if r == y])

        # Explode!
        if explode:
            while explode_count > 0:
                r = randint(1, y)
                if r < y:
                    explode_count -= 1
                rolls.append(r)

        ds.add('[')

        first = True
        for r in rolls:
            _add_roll(r, first)
            if first:
                first = False

        ds.add(']')

        if mod != 0:
            ds.add(f'{mod:+}')

        if len(dropped) > 0:
            ds.newline().toggle_strikethrough().add('Dropped: [')
        first = True
        for d in dropped:
            if first:
                first = False
            else:
                ds.add(', ')
            ds.add(str(d))

        if len(dropped) > 0:
            ds.add(']')
            ds.toggle_strikethrough()

        total = sum(rolls) + mod

        ds.newline().bold('Total').add(': ').add(str(total))

        return total, ds


def setup(bot):
    bot.add_cog(DiceCog(bot))
