from itertools import zip_longest
from discord.ext import commands


def safe_run(func):
    async def _do(self, ctx: commands.Context, *args, **kwargs):
        try:
            return await func(self, ctx, *args, **kwargs)
        except Exception as ex:
            print(ex)
            await ctx.send(f"Error: {ex}")

    return _do


def grouper(iterable, n, fillvalue=None):
    """Collect data into fixed-length chunks or blocks"""
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return zip_longest(*args, fillvalue=fillvalue)


def tablify(items, num_cols: int = 3, width_block: int = 4):
    num_rows = 0
    cols = [[] for _ in range(num_cols)]
    max_widths = [0 for _ in range(num_cols)]
    fmts = []

    for tup in grouper(map(str, items), num_cols, ''):
        num_rows += 1
        for idx, val in enumerate(tup):
            cols[idx].append(val)
            max_widths[idx] = max(max_widths[idx], len(val))
    for idx, mw in enumerate(max_widths):
        if mw < width_block:
            mw = width_block
        else:
            mod = mw % width_block
            mw += width_block if mod == 0 else mod

        max_widths[idx] = mw
        fmts.append("{:<%d}" % mw)

    for ridx in range(num_rows):
        s = ""
        for col, fmt in zip(cols, fmts):
            s += fmt.format(col[ridx])
        yield s.strip()


if __name__ == "__main__":
    print('\n'.join(tablify(['a', 'bbbbbbbbbbbbbbbbbbb', 'ccccc', 'ddddddddddd', 'e', 'fff'], 5)))
