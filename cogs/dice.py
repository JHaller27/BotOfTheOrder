from utils.discord_string import DiscordString
from random import randint
from discord.ext import commands
import re


class Roll:
    _value: int

    def __init__(self, size: int):
        self._size = size
        self._roll()

    def __repr__(self) -> str:
        return f"<Roll ({self._size})>"

    def __str__(self) -> str:
        return str(self.value)

    def __add__(self, other) -> int:
        if isinstance(other, Roll):
            return self.value + other.value

        return self.value + other

    def __radd__(self, other):
        return self.__add__(other)

    def __lt__(self, other):
        if isinstance(other, Roll):
            return self._value < other._value

        return self._value < other

    def _roll(self) -> None:
        self._value = randint(1, self._size)

    @property
    def value(self) -> int:
        return self._value

    def is_max(self) -> bool:
        return self._value == self._size

    def is_min(self) -> bool:
        return self._value == 1


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

        rolls = sorted([Roll(y) for _ in range(x)])
        dropped = []

        if drop < 0:
            rolls, dropped = rolls[drop:], rolls[:drop]
        elif drop > 0:
            rolls, dropped = rolls[:drop], rolls[drop:]

        def _add_roll(roll: Roll, is_first: bool) -> None:
            if not is_first:
                ds.add(' + ')
            if roll.is_max():
                ds.bold(roll)
                if explode:
                    ds.emoji('boom')
            elif roll.is_min():
                ds.bold(roll)
            else:
                ds.add(roll)

        # Prime explode count
        explode_rolls = []

        # Explode!
        if explode:
            explode_count = sum([1 for r in rolls if r.is_max()])
            while explode_count > 0:
                r = Roll(y)
                if not r.is_max():
                    explode_count -= 1
                explode_rolls.append(r)

        # Normal rolls
        first = True
        for r in rolls:
            _add_roll(r, first)
            if first:
                first = False

        # Modifier
        if mod > 0:
            ds.add(f' [+ {mod}]')
        elif mod < 0:
            ds.add(f' [- {mod}]')

        # Exploded dice
        if len(explode_rolls) > 0:
            ds.newline().bold('Explosion').add(': ')

            first = True
            for r in explode_rolls:
                _add_roll(r, first)
                if first:
                    first = False

        # Dropped rolls
        if len(dropped) > 0:
            ds.newline().toggle_italic().add('Dropped: (')
            first = True
            for d in dropped:
                if first:
                    first = False
                else:
                    ds.add(' + ')
                ds.add(str(d))

            ds.add(')').toggle_italic()

        # Total
        total = sum(rolls) + mod

        ds.newline().bold('Total').add(': ').add(total)

        return total, ds


def setup(bot):
    bot.add_cog(DiceCog(bot))
