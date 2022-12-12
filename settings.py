import os
from dotenv import load_dotenv
load_dotenv('.env')


BOT_TOKEN = os.getenv('BOT_TOKEN')
USERS = tuple(map(int, os.getenv('USERS').split()))
INTERVAL = os.getenv('INTERVAL')
