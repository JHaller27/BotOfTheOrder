from discord.ext import commands


def safe_run(func):
    async def _do(self, ctx: commands.Context, *args, **kwargs):
        try:
            return await func(self, ctx, *args, **kwargs)
        except Exception as ex:
            print(ex)
            await ctx.send(f"Error: {ex}")

    return _do
