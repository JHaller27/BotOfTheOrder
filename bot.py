import json
from discord.ext import commands
from pathlib import Path


class BotO(commands.Bot):
    # noinspection PyMethodMayBeStatic
    async def on_ready(self):
        print('Bot is ready!')


bot = BotO(command_prefix='/')
bot.load_extension('cogs.test')
bot.load_extension('cogs.dice')

# Load secrets
env_data_path = Path('.') / 'data' / 'secrets.json'
with open(env_data_path, 'r') as fp:
    secrets = json.load(fp)

# Run Bot
bot_token = secrets['DISCORD_TOKEN']
bot.run(bot_token)
