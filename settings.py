import os
from dotenv import load_dotenv
load_dotenv('.env')


BOT_TOKEN = os.getenv('BOT_TOKEN')
USER_ID = os.getenv('USER_ID')
INTERVAL = os.getenv('INTERVAL')
