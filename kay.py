import os
from datetime import datetime
import pytz
from aiogram import Bot
from dotenv import load_dotenv

load_dotenv()

tg_bot_api = os.getenv("tg_bot_api")
bot = Bot(token=tg_bot_api)
# timesone = pytz.timezone('Europe/Berlin')
# time_now_obj = datetime.now(timesone)
# time_now = time_now_obj.strftime('%d.%m.%Y %H:%M:%S')
# print(time_now)