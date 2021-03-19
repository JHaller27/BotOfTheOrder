from random import randint
from utils.discord_string import DiscordString
import re


DICE_REGEX = re.compile(r'(?P<num>\d+)d(?P<size>\d+)(?P<kd>[kd][hl]\d+)?(?P<explode>e)?(?P<mod>[+\-]\d+)?')


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


def roll_str(raw_str: str, mention=None) -> str:
    m = DICE_REGEX.search(raw_str)
    if m is not None:
        x = int(m['num'])
        y = int(m['size'])

        if x >= 10000:
            return "That roll is too powerful!"

        mod = 0
        drop = 0
        explode = m['explode'] is not None

        kd = m['kd']
        if kd is not None:
            drop = unify_keep_drop(kd[0] == 'k', kd[1] == 'h', int(kd[2:]), x)

        m = m['mod']
        if m is not None:
            mod = int(m)

        final_ds = DiscordString()
        if mention is not None:
            final_ds.add(mention).newline()

        rolls = roll(x, y, drop, explode)
        ds = print_rolls(rolls, mod, explode)
        final_ds += ds

        return str(final_ds)


def unify_keep_drop(keep: bool, highest: bool, count: int, total: int) -> int:
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


def roll(x: int, y: int, drop: int = 0, explode: bool = False) -> list:
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


def print_rolls(rolls, mod: int = 0, explode: bool = None, max_rolls: int = 100) -> DiscordString:
    ds = DiscordString()

    # Normal rolls
    ds.bold('Result').add(': (')

    if len(rolls) > max_rolls:
        rolls = [r for r in rolls if not r.dropped]

    if len(rolls) > max_rolls:
        ds.join(', ', rolls[:max_rolls], lambda r: r.dstr(explode))
        ds.add(', ...')
    else:
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
