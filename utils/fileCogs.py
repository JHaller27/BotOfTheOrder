from discord.ext import commands
import os


DATA_ROOT = "data"


class FileCog(commands.Cog):
    def __init__(self, bot: commands.Bot, name: str):
        self._bot = bot
        self._name = name

    def open(self, mode: str, *rest):
        path = self._get_path(rest)
        os.makedirs(os.path.dirname(path), exist_ok=True)

        return open(path, mode)

    def list(self, *parts):
        path = self._get_path(parts)
        return os.listdir(path)

    def _get_path(self, parts):
        path = os.path.join(DATA_ROOT, self._name, *parts)
        return path.lower()
