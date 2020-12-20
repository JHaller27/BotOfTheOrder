from pathlib import Path
from dotenv import load_dotenv
import os


ENV_DATA_PATH = Path('.') / 'data' / 'secrets.env'
load_dotenv(ENV_DATA_PATH)
BOT_TOKEN = os.getenv('TOKEN')

