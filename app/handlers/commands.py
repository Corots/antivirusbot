import logging
from aiogram import Router, Bot
from aiogram import types
from aiogram.filters.command import Command

from aiogram.fsm.context import FSMContext


from app.handlers.file_dialog import User, get_or_create_user
from app.keyboards.my_keyboards import get_language_keyboard
from app.texts import CommandText


router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message, bot: Bot):
    # Get the user from the database or add a new user if they don't exist
    # user = get_or_create_user(message.from_user.id)
    print("start command")
    """
    /start command handler for private chats
    :param message: Telegram message with "/start" command
    """
    user = get_or_create_user(message.from_user.id)
    await message.answer(
        CommandText.get_start_text(user.langenum),
    )


@router.message(Command("stop"))
async def cmd_stop(message: types.Message, state: FSMContext):
    """
    /stop command handler for private chats
    :param message: Telegram message with "/stop" command
    """
    await state.clear()
    await message.answer("Команда пока что не подключена")


@router.message(Command("about"))
async def cmd_about(message: types.Message):
    """
    /about command handler for private chats
    :param message: Telegram message with "/about" command
    """
    user = get_or_create_user(message.from_user.id)
    await message.answer(CommandText.get_about_text(user.langenum))


@router.message(Command("stats"))
async def cmd_about(message: types.Message):
    """
    /about command handler for private chats
    :param message: Telegram message with "/about" command
    """
    user: User = get_or_create_user(message.from_user.id)
    files_number = len(user.requests_today)
    links_number = len(user.linkrequests_today)

    await message.answer(
        CommandText.get_stats_text(user.langenum, files_number, links_number)
    )


@router.message(Command("settings"))
async def cmd_about(message: types.Message):
    """
    /about command handler for private chats
    :param message: Telegram message with "/about" command
    """
    user: User = get_or_create_user(message.from_user.id)

    await message.answer(
        "Choose language / Выберите язык",
        reply_markup=get_language_keyboard(user.langenum.value),
    )
