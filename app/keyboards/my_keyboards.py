from aiogram import types
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData

from aiogram.types import InlineKeyboardMarkup

from app.texts import LangEnum


from aiogram.utils.keyboard import InlineKeyboardBuilder


class CancelCB(CallbackData, prefix="cancCB"):
    req_id: int


def get_cancel_keyboard(req_id: int, filename: str, lang: LangEnum):
    builder = InlineKeyboardBuilder()

    if lang == LangEnum.russian:
        text = f"❌ Отменить проверку файла {filename}"
    else:
        text = f"❌ Cancel filecheck for {filename}"

    builder.button(text=text, callback_data=CancelCB(req_id=req_id).pack())
    return builder.as_markup()


def get_results_keyboard(link: str, lang: LangEnum):
    builder = InlineKeyboardBuilder()

    if lang == LangEnum.russian:
        text = f"🦠 Посмотреть результаты 🦠"
    else:
        text = f"🦠 Look for the results 🦠"

    builder.button(text=text, url=link)

    return builder.as_markup()


class CancelLinkCB(CallbackData, prefix="canclCB"):
    linkreq_id: int


def get_cancel_link_cb(linkreq_id: int, link: str, lang: LangEnum):

    if lang == LangEnum.russian:
        text = f"❌ Отменить проверку ссылки {link}"
    else:
        text = f"❌ Cancel check for link {link}"

    builder = InlineKeyboardBuilder()
    builder.button(text=text, callback_data=CancelLinkCB(linkreq_id=linkreq_id).pack())
    return builder.as_markup()


class LangCB(CallbackData, prefix="langcCB"):
    language: int


def get_language_keyboard(choosed: LangEnum):
    builder = InlineKeyboardBuilder()

    if choosed == LangEnum.russian.value:
        rus_text = "✅ Русский"
        eng_text = "English"
    elif choosed == LangEnum.english.value:
        rus_text = "Русский"
        eng_text = "✅ English"

    builder.button(
        text=rus_text, callback_data=LangCB(language=LangEnum.russian.value).pack()
    )
    builder.button(
        text=eng_text, callback_data=LangCB(language=LangEnum.english.value).pack()
    )

    return builder.as_markup()
