import os
import sys
from discord.ext import commands


class BotO(commands.Bot):
    # noinspection PyMethodMayBeStatic
    async def on_ready(self):
        print(f"Bot is ready using prefix '{self.command_prefix}'")


prefix = os.environ.get('DISCORD_PREFIX') or '/'
bot = BotO(command_prefix=prefix)
bot.load_extension('cogs.test')
bot.load_extension('cogs.dice')
# bot.load_extension('cogs.triangulate')
bot.load_extension('cogs.troika')

# Run Bot
token_env_name = 'DISCORD_TOKEN'
bot_token = os.environ.get(token_env_name)
if bot_token is None:
    print(f"'{token_env_name}' not found in environment. Failed to start bot.", file=sys.stderr)
    sys.exit(1)
bot.run(bot_token)
