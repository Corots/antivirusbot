from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.handlers.file_dialog import User

scheduler = AsyncIOScheduler()


class Sheduler():

    async def sh_method(self):
        pass

    async def method(self):
        users_today = User.joined_today()
        all_users = User.all_users()

        text = f"Today joined {len(users_today)} users"

        for id, user in enumerate(users_today):
            text += f"\ntelegram id : {user.telegram_id}  | Дата: {user.datejoin}"

        text += "\n\n\n<b>Отчет за день:</b>"
        for id, user in enumerate(all_users):
            text += f"\nПользователь {id + 1} : id {user.telegram_id} \n   Запросов файлов : {len(user.requests_today)} \n   Запросов ссылок : {len(user.linkrequests_today)}\n"

        await self.bot.send_message(chat_id=919543660, text = text)

    def __init__(self, bot : Bot) -> None:
        self.scheduler = AsyncIOScheduler()
        # Interval sheduler
        # self.scheduler.add_job(self.method, 'interval', hours = 1, id='my_job_id1')

        # Cron sheduler
        self.scheduler.add_job(self.method, 'cron', hour = 10, id='my_job_id5')

        # Our bot
        self.bot = bot

    # Method to start scheduler
    async def start_shedule(self):
        self.scheduler.start()

    
