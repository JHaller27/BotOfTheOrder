from discord.ext import commands
import os


DATA_ROOT = os.environ.get("BOTO_DATA") or "data"
print(f"Using data path '{DATA_ROOT}'")
ILLEGAL_PATH_CHARS = ' /\\'


def sanitize_part(part: str) -> str:
    part = str(part)
    for ipc in ILLEGAL_PATH_CHARS:
        part = part.replace(ipc, '_')
    return part


class FileCog(commands.Cog):
    def __init__(self, bot: commands.Bot, name: str):
        self._bot = bot
        self._name = name

    def open(self, mode: str, *rest):
        path = self.get_path(rest)
        return open(path, mode)

    def open_user(self, mode: str, ctx: commands.Context, *parts):
        path = self.get_path([ctx.author.id, *parts])
        return open(path, mode)

    def list(self, *parts):
        path = self.get_path(parts)
        return os.listdir(path)

    def list_user(self, ctx: commands.Context, *parts):
        path = self.get_path([ctx.author.id, *parts])
        return os.listdir(path)

    def delete(self, *parts):
        path = self.get_path(parts)
        os.remove(path)

    def delete_user(self, ctx: commands.Context, *parts):
        path = self.get_path([ctx.author.id, *parts])
        os.remove(path)

    def get_path(self, parts):
        path = os.path.join(DATA_ROOT, self._name)
        if len(parts) > 0:
            parts = map(sanitize_part, parts)
            path = os.path.join(path, *parts)
        path = path.lower()
        os.makedirs(os.path.dirname(path), exist_ok=True)

        return path
