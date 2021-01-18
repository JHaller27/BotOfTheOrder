from discord.ext import commands
import os


DATA_ROOT = "data"
ILLEGAL_PATH_CHARS = ' /\\'


def sanitize_part(part: str) -> str:
    for ipc in ILLEGAL_PATH_CHARS:
        part = part.replace(ipc, '_')
    return part


class FileCog(commands.Cog):
    def __init__(self, bot: commands.Bot, name: str):
        self._bot = bot
        self._name = name

    def open(self, mode: str, *rest):
        path = self._get_path(rest)
        return open(path, mode)

    def open_user(self, ctx: commands.Context, *parts):
        path = self._get_path([ctx.author.id, *parts])
        return open(path, mode)

    def list(self, *parts):
        path = self._get_path(parts)
        return os.listdir(path)

    def _get_path(self, parts):
        parts = map(sanitize_part, parts)
        path = os.path.join(DATA_ROOT, self._name, *parts)
        path = path.lower()
        os.makedirs(os.path.dirname(path), exist_ok=True)

        return path
