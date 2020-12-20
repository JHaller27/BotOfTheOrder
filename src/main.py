import json
import discord
from pathlib import Path


client = discord.Client()


@client.event
async def on_ready():
    print('Bot is ready!')


env_data_path = Path('..') / 'data' / 'secrets.json'
with open(env_data_path, 'r') as fp:
    secrets = json.load(fp)

BOT_TOKEN = secrets['DISCORD_TOKEN']
client.run(BOT_TOKEN)
