from utils.discord_string import DiscordString
from discord.ext import commands
from discord import File
import os

from triangulate_wallpaper.canvas import MosaicCanvas
from triangulate_wallpaper.painters import UrlTemplatePainter, NoisyPainter
from triangulate_wallpaper.graph import ScatterGraph


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

        try:
            canvas.draw_graph(graph, ['color'])
        except Exception as ex:
            await ctx.send(str(ex))
            return

        path = os.path.join('.', 'data', f'triangles_{ctx.author}_{img_width}x{img_height}.png')
        canvas.save_to(path)

        ds = DiscordString()
        ds.add(ctx.message.author.mention).newline().pre(url)
        await ctx.send(str(ds), file=File(path))
        await ctx.message.delete()

        if os.path.exists(path):
            os.remove(path)


def setup(bot):
    bot.add_cog(Triangulate(bot))
