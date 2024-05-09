from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats


async def set_bot_commands(bot: Bot):
    data = [
        # Commands in private chats (English and Russian)
        (
            [
                BotCommand(command="start", description="Start Bot"),
                BotCommand(command="stats", description="My statistic"),
                BotCommand(command="settings", description="My settings"),
                # BotCommand(command="stop", description="Stop Bot"),
                BotCommand(command="about", description="Info about Bot"),
            ],
            BotCommandScopeAllPrivateChats(),
            "en"
        ),
        (
            [
                BotCommand(command="start", description="Запустить Бота"),
                BotCommand(command="stats", description="Моя статистика"),
                BotCommand(command="settings", description="Мои настройки"),
                # BotCommand(command="stop", description="Остановить Бота"),
                BotCommand(command="about", description="Информация о Боте"),
            ],
            BotCommandScopeAllPrivateChats(),
            "ru"
        ),
        # # Commands in (super)groups (English and Russian)
        # (
        #     [BotCommand(command="id", description="Print Telegram ID of this group chat")],
        #     BotCommandScopeAllGroupChats(),
        #     "en"
        # ),
        # (
        #     [BotCommand(command="id", description="Узнать ID этой группы")],
        #     BotCommandScopeAllGroupChats(),
        #     "ru"
        # ),
    ]

    for commands_list, commands_scope, language in data:
        await bot.set_my_commands(commands=commands_list, scope=commands_scope, language_code=language)