from dotenv import load_dotenv

import json
import os

load_dotenv('secrets/.env')

MEMAS_ID = int(os.getenv('MEME_CHANNEL_ID')) # type: ignore[valid-type]
# It's only in seppuku.py but it may be needed in other files too

with open('database/commands.json') as f:
    TEMPLATE = json.load(f)