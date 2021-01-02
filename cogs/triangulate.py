from utils.discord_string import DiscordString
from discord.ext import commands
from discord import File
import os

# TODO import from separate repo - this is copy+pasted
from triangulate_wallpaper import MosaicCanvas, UrlTemplatePainter, NoisyPainter, ScatterGraph


# noinspection PyTypeChecker
class Triangulate(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self._bot = bot

    @commands.command()
    async def triangulate(self, ctx: commands.Context, url: str) -> None:
        img_width, img_height = 1920, 1080
        count, margin = 200, 20

        painter = UrlTemplatePainter(img_width, img_height, url)
        painter = NoisyPainter(painter, [20])
        canvas = MosaicCanvas(painter, width=img_width, height=img_height)

        graph = ScatterGraph(img_width, img_height, count, margin)
        graph.triangulate()

        canvas.draw_graph(graph, ['color'])

        path = os.path.join('.', 'data', f'triangles_{ctx.author}_{img_width}x{img_height}.png')
        canvas.save_to(path)

        await ctx.message.delete()
        ds = DiscordString()
        ds.add(ctx.message.author.mention).newline().pre(url)
        await ctx.send(str(ds), file=File(path))

        if os.path.exists(path):
            os.remove(path)


def setup(bot):
    bot.add_cog(Triangulate(bot))
