import asyncio
import logging
import sys

# from app.scheduler.my_schedule import Sheduler
from config.config_reader import config

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.handlers import commands, file_dialog


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(
        token=config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    # And the run events dispatching
    dp.include_router(commands.router)
    dp.include_router(file_dialog.router)

    logging.info("Start polling")
    # remove all pollings in queue
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
