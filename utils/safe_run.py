from discord.ext import commands


async def safe_run(callback, ctx: commands.Context, *args, **kwargs):
    try:
        await callback(ctx, *args, **kwargs)
    except Exception as ex:
        print(f"Error in {callback.__name__}")
        await ctx.send(f"Command failed: {ex}")
        print(ex)
