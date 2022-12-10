import asyncio

from aiogram.utils import executor
from loguru import logger

import aiohttp
from bs4 import BeautifulSoup

from database import Database
from loader import bot
from models import App
from handlers import *
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from settings import USER_ID, INTERVAL

BASE_LINK = "https://play.google.com"


def get_apps_for_developer(html_text: str, dev_id: str):
    soup = BeautifulSoup(html_text, 'html.parser')
    apps = soup.find_all(class_="ULeU3b")
    apps_list = []
    for i in apps:
        try:
            game_name = i.find(class_="ubGTjb").span.text
            game_link = i.find("a", href=True)['href']
            app = App(name=game_name, link=f"{BASE_LINK}{game_link}", author=dev_id)
            apps_list.append(app)
        except AttributeError:
            temp = i.find('a')
            if temp is None:
                continue
            game_link = temp['href']
            title = temp.find(class_="Epkrse").text
            app = App(name=title, link=f'{BASE_LINK}{game_link}', author=dev_id)
            apps_list.append(app)

    return apps_list


async def get_page_for_developer(session: aiohttp.ClientSession, dev_id: str):
    url = f"https://play.google.com/store/apps/developer?id={dev_id}"
    url2 = f"https://play.google.com/store/apps/dev?id={dev_id}"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru"
    }
    async with session.get(url, headers=headers) as resp:
        if resp.status == 404:
            async with session.get(url2, headers=headers) as resp2:
                return await resp2.text()
        return await resp.text()


async def get_data_from_page(session: aiohttp.ClientSession, dev_id: str):
    data = await get_page_for_developer(session, dev_id)
    apps = get_apps_for_developer(data, dev_id)
    return apps


async def fetch_all(session: aiohttp.ClientSession, devs_list: tuple):
    tasks = []
    for dev_id in devs_list:
        task = asyncio.create_task(get_data_from_page(session, dev_id))
        tasks.append(task)
    result = await asyncio.gather(*tasks)
    return result


async def main():
    logger.info(f"Start script")
    async with aiohttp.ClientSession() as session:
        res = await fetch_all(session, get_devs_list('devs.txt'))
    for apps in res:
        for app in apps:
            if not db.is_app_exists(app):
                db.add_app(app)
                message = f"Новое приложение от разработчика {app.author}!\n{app.name} {app.link}"
                await bot.send_message(USER_ID, message)


def get_devs_list(filename: str):
    with open(filename, 'r') as file:
        devs = [i.strip()[i.find("id=")+3:] for i in file.readlines()]
        return tuple(devs)


if __name__ == "__main__":
    logger.add("logs/error.log", format="{time} {level} {message}", level="ERROR", rotation="01:00")
    logger.add("logs/info.log", format="{time} {level} {message}", level="INFO", rotation="01:00")
    db = Database()
    logger.info("Start bot")
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(main, trigger='interval', minutes=INTERVAL)
    scheduler.start()
    executor.start_polling(dp)


