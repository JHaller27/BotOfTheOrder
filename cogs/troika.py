from discord.ext import commands
from utils.fileCogs import FileCog
from utils.discord_string import DiscordString
import utils.dice as dice
import random


class Troika(FileCog):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot, 'troika')

    @commands.group()
    async def troika(self, ctx: commands.Context):
        pass

    @troika.command()
    async def foo(self, ctx: commands.Context) -> None:
        print(ctx.author.name)
        await ctx.send('bar')

    @troika.command()
    async def save(self, ctx: commands.Context, msg: str) -> None:
        name = ctx.author.name
        with self.open('w', f'{name}.txt') as fp:
            fp.write(msg)
        await ctx.send('saved')

    @troika.command()
    async def load(self, ctx: commands.Context) -> None:
        name = ctx.author.name
        with self.open('r', f'{name}.txt') as fp:
            msg = fp.read()
        await ctx.send(msg)

    @troika.command()
    async def add_weapon(self, ctx: commands.Context, name: str, *rolls):
        with self.open('w', 'weapon', name) as fp:
            fp.write(','.join(rolls))
        await ctx.send(f'Saved weapon "{name}" with {len(rolls)} rolls')

    @troika.command()
    async def list_weapons(self, ctx: commands.Context):
        ds = DiscordString()
        ds.join(', ', sorted(self.list('weapon')))
        await ctx.send(str(ds))

    @troika.command()
    async def damage(self, ctx: commands.Context, name: str):
        try:
            with self.open('r', 'weapon', name) as fp:
                rolls = fp.read().split(',')
        except FileNotFoundError:
            await ctx.send(f'Weapon "{name}" not found')
            return

        idx = random.randrange(0, 6)
        ds_rolls = []
        for i, r in enumerate(rolls):
            if i == idx:
                ds_rolls.append(DiscordString().bold(r))
            else:
                ds_rolls.append(DiscordString(r))
        ds = DiscordString().join(', ', ds_rolls, key=str)

        await ctx.send(str(ds))

    @troika.command()
    async def attack(self, ctx: commands.Context, mod: str = None):
        dice_str = '2d6'
        if mod is not None:
            mod = int(mod)
            dice_str += f'{mod:+}'
        await ctx.send(dice.roll_str(dice_str))


def setup(bot):
    bot.add_cog(Troika(bot))
