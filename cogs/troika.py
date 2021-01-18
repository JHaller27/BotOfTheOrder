from discord.ext import commands
from utils.fileCogs import FileCog
from utils.discord_string import DiscordString
import utils.dice as dice
import random


class Troika(FileCog):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot, 'troika')
        self._combat_bag = []
        self._combat_drawn = []
        self._init_combat()

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
        await self.roll(ctx, mod)

    @troika.command()
    async def oops(self, ctx: commands.Context):
        with self.open('r', 'oops') as fp:
            results = [line.strip() for line in fp]
        choice = random.choice(results)

        ds = DiscordString()
        ds.emoji('sparkles').bold("OOPS!").emoji('boom').newline()
        ds.add(choice)

        await ctx.send(str(ds))

    @troika.command()
    async def roll(self, ctx: commands.Context, mod: str = None):
        dice_str = '2d6'
        if mod is not None:
            mod = int(mod)
            dice_str += f'{mod:+}'
        await ctx.send(dice.roll_str(dice_str))

    @troika.command()
    async def combat(self, ctx: commands.Context, *args):
        cmd, args = args[0], args[1:]
        cmd_map = {
            'add': self.combat_add,
            'show': self.combat_show,
            'clear': self.combat_clear,
            'reset': self.combat_reset,
            'draw': self.combat_draw,
        }

        if cmd not in cmd_map:
            ds = DiscordString()
            ds.italic(f'Invalid combat command: "{cmd}"').newline()
            ds.add('Valid commands: ').toggle_pre_line().join(', ', sorted(cmd_map.keys())).toggle_pre_line()
            await ctx.send(str(ds))

        fn = cmd_map[cmd]

        # noinspection PyUnresolvedReferences,PyArgumentList
        await fn(ctx, *args)

    async def combat_add(self, ctx: commands.Context, *args):
        count = 1
        for a in args:
            if a.isnumeric():
                count = int(a)
            else:
                for _ in range(count):
                    self._combat_bag.append(a)
                await ctx.send(f'Added {count}x {a}')
                count = 1

    async def combat_show(self, ctx: commands.Context, *args):
        sep = ', '

        ds = DiscordString()
        if len(self._combat_drawn) > 0:
            ds.toggle_italic()
            ds.bold('Gone:').add(' ').join(sep, self._combat_drawn)
            ds.toggle_italic()

            ds.newline()

        ds.bold('Bag:').add(' ').join(sep, self._combat_bag)

        await ctx.send(str(ds))

    async def combat_clear(self, ctx: commands.Context, *args):
        self._init_combat()
        self._combat_drawn.clear()
        await ctx.send('Combat hat cleared')

    async def combat_reset(self, ctx: commands.Context, *args):
        for c in self._combat_drawn:
            self._combat_bag.append(c)
        self._combat_drawn.clear()
        await ctx.send('Combat hat reset')

    async def combat_draw(self, ctx: commands.Context, *args):
        combatant = random.choice(self._combat_bag)
        self._combat_bag.remove(combatant)
        self._combat_drawn.append(combatant)

        await ctx.send(combatant)

        if combatant == 'END':
            await self.combat_reset(ctx)

    def _init_combat(self):
        self._combat_bag.clear()
        self._combat_bag.append('END')


def setup(bot):
    bot.add_cog(Troika(bot))
