import json
from discord.ext import commands
from pathlib import Path


bot = commands.Bot(command_prefix='/')


@bot.event
async def on_ready():
    print('Bot is ready!')


bot.load_extension('cogs.test')

# Load secrets
env_data_path = Path('.') / 'data' / 'secrets.json'
with open(env_data_path, 'r') as fp:
    secrets = json.load(fp)

# Run Bot
bot_token = secrets['DISCORD_TOKEN']
bot.run(bot_token)
