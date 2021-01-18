from discord.ext import commands
from utils.fileCogs import FileCog
from utils.discord_string import DiscordString
import utils.dice as dice
import random
import json


class Resource:
    def __init__(self, max_val, curr_val=None):
        self.max = max_val
        self.curr = curr_val if curr_val is not None else max_val

    def __add__(self, other: int):
        return Resource(self.max, min(self.max, self.curr + other))

    def __radd__(self, other: int) -> int:
        return other + self.curr

    def __sub__(self, other: int):
        return Resource(self.max, max(self.max, self.curr - other))

    def __rsub__(self, other: int):
        return other - self.curr

    def __str__(self) -> str:
        return f'{self.curr}/{self.max}'

    @classmethod
    def from_dict(cls, j: dict) -> 'Resource':
        i = cls(j.get('max'), j.get('current'))
        return i

    def to_dict(self) -> dict:
        return {'max': self.max, 'current': self.curr}


class Character:
    def __init__(self, name: str, stats=None):
        self.name = name
        if stats is None:
            self.skill = 4
            self.stamina = Resource(14)
            self.luck = Resource(7)
        else:
            self.skill = stats[0]
            self.stamina = Resource(stats[1])
            self.luck = Resource(stats[2])

    @classmethod
    def roll(cls, name: str) -> 'Character':
        i = cls(name)
        i.skill = sum(dice.roll(1, 3)) + 3
        i.stamina = Resource( sum(dice.roll(2, 6)) + 12 )
        i.luck = Resource( sum(dice.roll(1, 6)) + 6 )
        return i

    @classmethod
    def from_dict(cls, j: dict) -> 'Character':
        i = cls(j.get('name'))
        i.skill = j.get('skill')
        i.stamina = Resource.from_dict( j.get('stamina') )
        i.luck = Resource.from_dict( j.get('luck') )
        return i

    def to_dict(self) -> dict:
        return {
                'name': self.name,
                'skill': self.skill,
                'stamina': self.stamina.to_dict(),
                'luck': self.luck.to_dict(),
               }

    def __str__(self) -> str:
        return f'<Character name={self.name} ({str(self.skill)}, {str(self.stamina)}, {str(self.luck)})>'


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

    @troika.command()
    async def add_character(self, ctx: commands.Context, name: str, *args):
        if len(args) == 0:
            c = Character(name)
        elif args[0] == 'roll':
            c = Character.roll(name)
        elif len(args) == 3:
            c = Character(name, (int(args[0]), int(args[1]), int(args[2])))
        else:
            await ctx.send('Character format not recognized')
            return

        self._save_character(ctx, c)

        ds = DiscordString()
        ds.add(f'Saved character "{name}" for ').add(ctx.author.mention)

        await ctx.send(str(ds))

        await self.whoami(ctx)

    @troika.command()
    async def load_character(self, ctx: commands.Context, name: str):
        with self.open_user('r', ctx, 'character', name) as fp:
            obj = json.load(fp)
        c = Character.from_dict(obj)

        with self.open_user('w', ctx, 'curr_character') as fp:
            fp.write(c.name)

        ds = DiscordString()
        ds.add(f'Loaded character "{c.name}" for ').add(ctx.author.mention)

        await ctx.send(str(ds))

    @troika.command()
    async def whoami(self, ctx: commands.Context):
        c = self._get_character(ctx)

        ds = DiscordString()
        ds.bold(c.name).newline()
        ds.toggle_pre_block()
        ds.add('Skill   | ').add(c.skill).newline()
        ds.add('Stamina | ').add(c.stamina).newline()
        ds.add('Luck    | ').add(c.luck).newline()
        ds.toggle_pre_block()

        await ctx.send(str(ds))

    def _get_character(self, ctx: commands.Context) -> Character:
        with self.open_user('r', ctx, 'curr_character') as fp:
            name = fp.read()
        name = name.strip()

        with self.open_user('r', ctx, 'character', name) as fp:
            obj = json.load(fp)
        c = Character.from_dict(obj)

        return c

    def _save_character(self, ctx: commands.Context, c: Character):
        name = c.name
        obj = c.to_dict()

        with self.open_user('w', ctx, 'character', name) as fp:
            json.dump(obj, fp)

        with self.open_user('w', ctx, 'curr_character') as fp:
            fp.write(name)

    @troika.command()
    async def list_characters(self, ctx: commands.Context):
        try:
            char_list = self.list_user(ctx, 'character')
        except FileNotFoundError:
            await ctx.send('No characters yet!')
            return

        def _get_name(fname: str) -> str:
            try:
                with self.open_user('r', ctx, 'character', fname) as fp:
                    obj = json.load(fp)
                c = Character.from_dict(obj)
                name = c.name
            except (FileNotFoundError, json.JSONDecodeError):
                name = fname

            return name

        ds = DiscordString().join(', ', map(_get_name, char_list))

        await ctx.send(str(ds))

    @troika.command()
    async def skill(self, ctx: commands.Context):
        rolls = dice.roll(2, 6)
        roll_sum = sum(rolls)
        character = self._get_character(ctx)
        target = character.skill

        ds = DiscordString()
        ds.add(ctx.author.mention).newline()
        ds.add(character.name)
        if roll_sum <= target:
            ds.bold(' succeeds')
        else:
            ds.bold(' fails')
        ds.add('!').newline()

        ds.toggle_italic()
        ds.add('(').join(', ', rolls).add(') ').add(roll_sum).add(' ')
        ds.toggle_italic()
        ds.emoji('game_die')
        ds.italic(f' vs {target}')

        await ctx.send(str(ds))

    @troika.command()
    async def luck(self, ctx: commands.Context, mod: str = None):
        if mod is None:
            await self._roll_luck(ctx)
            return

        if mod.startswith('+') or mod.startswith('-'):
            c = self._get_character(ctx)
            c.luck.curr += int(mod)
            self._save_character(ctx, c)
        else:
            c = self._get_character(ctx)
            c.luck.curr = int(mod)
            self._save_character(ctx, c)

        ds = DiscordString()
        ds.bold('Luck: ').add(str(c.luck))

        await ctx.send(str(ds))

    async def _roll_luck(self, ctx: commands.Context):
        rolls = dice.roll(2, 6)
        roll_sum = sum(rolls)
        character = self._get_character(ctx)
        target = character.luck.curr

        character.luck.curr -= 1
        self._save_character(ctx, character)

        ds = DiscordString()
        ds.add(ctx.author.mention).newline()
        ds.add(character.name)
        if roll_sum <= target:
            ds.bold(' succeeds')
        else:
            ds.bold(' fails')
        ds.add('!').newline()

        ds.toggle_italic()
        ds.add('(').join(', ', rolls).add(') ').add(roll_sum).add(' ')
        ds.toggle_italic()
        ds.emoji('game_die')
        ds.italic(f' vs {target}').newline()
        ds.add('Luck: ').add(str(character.luck))

        await ctx.send(str(ds))

    @troika.command()
    async def stamina(self, ctx: commands.Context, mod: str):
        if mod.startswith('+') or mod.startswith('-'):
            c = self._get_character(ctx)
            c.stamina.curr += int(mod)
            self._save_character(ctx, c)
        else:
            c = self._get_character(ctx)
            c.stamina.curr = int(mod)
            self._save_character(ctx, c)

        ds = DiscordString()
        ds.bold('Stamina: ').add(str(c.stamina))

        await ctx.send(str(ds))

    async def rest(self, ctx: commands.Context):
        rolls = dice.roll(2, 6)
        roll_sum = sum(rolls)

        c = self._get_character(ctx)
        restore = roll_sum
        if c.stamina.curr + restore > c.stamina.max:
            restore = c.stamina.max - c.stamina.curr
        c.stamina.curr += restore
        self._save_character(ctx, c)

        ds = DiscordString()
        ds.add('8 hours pass').newline()
        ds.add('Restored ').bold(restore).add(' stamina').newline()
        ds.bold('Stamina: ').add(str(c.luck))
        ds.toggle_italic()
        ds.add('(').join(', ', rolls).add(') ').add(roll_sum).add(' ')
        ds.toggle_italic()
        ds.emoji('game_die')

        await ctx.send(str(ds))


def setup(bot):
    bot.add_cog(Troika(bot))
