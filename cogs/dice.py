from utils.discord_string import DiscordString
from random import randint
from discord.ext import commands
import re


class Roll:
    _size: int
    _value: int
    _dropped: bool

    def __init__(self, size: int):
        self._size = size
        self._roll()

        self._dropped = False

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
        return 0 if self._dropped else self._value

    @property
    def dropped(self) -> bool:
        return self._dropped

    def dstr(self, explode: bool) -> DiscordString:
        ds = DiscordString()

        if self.dropped:
            ds.strikethrough(self._value)

        elif self.is_max():
            ds.bold(self._value)
            if explode:
                ds.emoji('boom')

        elif self.is_min():
            ds.bold(self._value)

        else:
            ds.add(self._value)

        return ds

    def is_max(self) -> bool:
        return not self._dropped and self._value == self._size

    def is_min(self) -> bool:
        return self._value == 1

    def explode(self) -> 'Roll':
        return Roll(self._size)

    def drop(self) -> None:
        self._dropped = True


class DiceCog(commands.Cog):
    DICE_REGEX = re.compile(r'(?P<num>\d+)d(?P<size>\d+)(?P<kd>[kd][hl]\d+)?(?P<explode>e)?(?P<mod>[+\-]\d+)?')
    OL_ACTION_REGEX = re.compile(r'(?P<score>\d+)?(?P<adv>[ad]\d+)?(?P<mod>[+\-]\d+)?')

    OL_ATTR_DICE_MAP = [
        (0, 0),
        (1, 4),
        (1, 6),
        (1, 8),
        (1, 10),
        (2, 6),
        (2, 8),
        (2, 10),
        (3, 8),
        (3, 10),
        (4, 8),
    ]

    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.group()
    async def ol(self, ctx: commands.Context):
        pass

    @ol.command()
    async def action(self, ctx: commands.Context, roll_str: str = ''):
        if m := DiceCog.OL_ACTION_REGEX.search(roll_str):
            score = 0
            adv = 0
            mod = 0

            if x := m['score']:
                score = int(x)

            if x := m['adv']:
                x = x.lower()
                adv = int(x[1:])
                if x[0] == 'd':
                    adv = -adv

            if x := m['mod']:
                mod = int(x)

            all_dice = [(1, 20)]
            mod_dice = DiceCog.OL_ATTR_DICE_MAP[score]
            if mod_dice[0] != 0:
                all_dice.append(mod_dice)

            all_results = []
            ds = DiscordString()
            ds.add(ctx.message.author.mention).newline().bold('Rolling').add(': ')

            rolls = []

            # Roll first set of dice
            for x, y in all_dice[:-1]:
                ds.add(f'{x}d{y} + ')

                rolls.extend(DiceCog._roll(x, y, 0, True))

                result = sum(rolls)

                all_results.append(result)

            # Get+adjust dice for last roll
            og_x, y = all_dice[-1]
            x = og_x + abs(adv)

            ds.add(f'{x}d{y}')
            if adv > 0:
                ds.add(f'dl{adv}')
            elif adv < 0:
                ds.add(f'dh{-adv}')

            if mod > 0:
                ds.add(f' + {mod}')
            elif mod < 0:
                ds.add(f' - {-mod}')

            if adv < 0:
                drop = DiceCog._unify_keep_drop(False, True, -adv, x)
            elif adv > 0:
                drop = DiceCog._unify_keep_drop(False, False, adv, x)
            else:
                drop = 0

            rolls.extend(DiceCog._roll(x, y, drop, True))

            ds.newline()
            ds += DiceCog._print_rolls(rolls, mod, True)

            await ctx.send(str(ds))

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

            final_ds = DiscordString()
            final_ds.add(ctx.message.author.mention).newline()

            rolls = DiceCog._roll(x, y, drop, explode)
            ds = DiceCog._print_rolls(rolls, mod, explode)
            final_ds += ds

            await ctx.send(str(final_ds))

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
    def _roll(x: int, y: int, drop: int, explode: bool) -> list:
        rolls = [Roll(y) for _ in range(x)]

        dropped = []
        if drop < 0:
            dropped = sorted(rolls)[:drop]
        elif drop > 0:
            dropped = sorted(rolls)[drop:]

        for d in dropped:
            d.drop()

        # Explode!
        if explode:
            explodable_rolls = list([r for r in rolls if r.is_max()])
            while len(explodable_rolls) > 0:
                r = explodable_rolls.pop().explode()
                if r.is_max():
                    explodable_rolls.append(r)
                rolls.append(r)

        return rolls

    @staticmethod
    def _print_rolls(rolls, mod: int, explode: bool) -> DiscordString:
        ds = DiscordString()

        # Normal rolls
        ds.bold('Result').add(': (')

        ds.join(', ', rolls, lambda r: r.dstr(explode))

        ds.add(')')

        # Modifier
        if mod > 0:
            ds.add(f' + {mod}')
        elif mod < 0:
            ds.add(f' - {-mod}')

        # Total
        total = sum(rolls) + mod

        ds.newline().bold('Total').add(': ').add(total).add(' ').emoji('game_die')

        return ds


def setup(bot):
    bot.add_cog(DiceCog(bot))
