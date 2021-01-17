from discord.ext import commands
from cogs.utils.fileCogs import FileCog


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


def setup(bot):
    bot.add_cog(Troika(bot))
