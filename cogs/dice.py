from utils.discord_string import DiscordString
import utils.dice as dice
from discord.ext import commands
import re


class DiceCog(commands.Cog):
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

            if score == 69:
                await ctx.send("Nice")
                return

            if score >= len(DiceCog.OL_ATTR_DICE_MAP):
                await ctx.send("Your action is too powerful!")
                return

            if score < 0:
                await ctx.send("Your action isn't powerful enough")
                return

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

                rolls.extend(dice.roll(x, y, 0, True))

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
                drop = dice.unify_keep_drop(False, True, -adv, x)
            elif adv > 0:
                drop = dice.unify_keep_drop(False, False, adv, x)
            else:
                drop = 0

            rolls.extend(dice.roll(x, y, drop, True))

            ds.newline()
            ds += dice.print_rolls(rolls, mod, True)

            await ctx.send(str(ds))

    @commands.command()
    async def roll(self, ctx: commands.Context, roll_str: str):
        if result := dice.roll_str(roll_str, ctx.author.mention):
            await ctx.send(result)


def setup(bot):
    bot.add_cog(DiceCog(bot))
