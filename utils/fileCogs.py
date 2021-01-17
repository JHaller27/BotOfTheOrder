from discord.ext import commands
import os


DATA_ROOT = "data"


class FileCog(commands.Cog):
    def __init__(self, bot: commands.Bot, name: str):
        self._bot = bot
        self._name = name

    def open(self, mode: str, *rest):
        path = os.path.join(DATA_ROOT, self._name, *rest)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print(f'Saving to {path}...')

        return open(path, mode)
