from aiogram import Router, Bot, F
from aiogram import types, html
from aiogram.filters.command import Command
from aiogram.filters.state import StatesGroup, State

from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest
import aiohttp
import asyncio
import logging
import requests
from urllib.parse import urlparse

import sqlalchemy
from app.texts import CheckTypeEnum, FileDialogText, LangEnum

from config.config_reader import config


import json


from app.filters.chat_type import ChatTypeFilter
from app.keyboards.my_keyboards import (
    CancelCB,
    LangCB,
    get_cancel_keyboard,
    get_language_keyboard,
    get_results_keyboard,
)
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Boolean,
    BigInteger,
    func,
    update,
)
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timedelta
from app.db.settings import session, engine
from sqlalchemy.orm import Mapped, Relationship


from emoji import emoji_list
from sqlalchemy.exc import InvalidRequestError

# Rate limiting parameters
MAX_FILES_PER_DAY = 120
MAX_LINKS_PER_DAY = 120
MINIMUM_DELAY_SECONDS = 15
MAX_REQUESTS_PER_DAY = 500
API_KEY = config.virustotal_api

router = Router()


class MySG(StatesGroup):
    main = State()


# Initialize the database engine and session
Base = declarative_base()


# Define the User and Request models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    language = Column(Integer, nullable=False, default=2)

    requests: 'Relationship[list["Request"]]' = relationship(
        "Request", back_populates="user"
    )
    linkrequests: 'Relationship[list["LinkRequest"]]' = relationship(
        "LinkRequest", back_populates="user"
    )
    # queue_requests: 'Relationship[list["Queue"]]' = relationship(
    #     "Queue", back_populates="user"
    # )
    # linkqueue_requests: 'Relationship[list["LinkQueue"]]' = relationship(
    #     "LinkQueue", back_populates="user"
    # )

    datejoin = Column(DateTime, default=datetime.now)

    @property
    def requests_today(self):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if len(self.requests) == 0:
            logging.info("No requests")
            return []

        logging.info("Requests exist")
        # and request.result
        return [request for request in self.requests if request.date >= today]

    def joined_today():
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        return session.query(User).where(User.datejoin > today).all()

    def all_users() -> list["User"]:
        return session.query(User).all()

    @property
    def linkrequests_today(self):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        if len(self.linkrequests) == 0:
            return []

        return [
            linkrequests
            for linkrequests in self.linkrequests
            if linkrequests.date >= today and linkrequests.result
        ]

    @property
    def langenum(self):
        if self.language == LangEnum.russian.value:
            return LangEnum.russian
        else:
            return LangEnum.english

    @langenum.setter
    def langenum(self, lang: LangEnum):
        if lang == LangEnum.russian:
            self.language = 1
        else:
            self.language = 2


class BaseRequest(Base):
    __abstract__ = True

    virustotalid = Column(String)
    result = Column(Boolean)
    link = Column(String)
    date = Column(DateTime, default=datetime.now)
    finished = Column(Boolean, nullable=False, default=False)
    attempts = Column(Integer, nullable=False, default=1)
    messageid = Column(BigInteger)
    replyid = Column(BigInteger)
    user_id = Column(Integer, ForeignKey("users.id"))


class Request(BaseRequest):
    __tablename__ = "requests"
    id = Column(Integer, primary_key=True)
    filename = Column(String, nullable=False)
    filesize = Column(Integer, nullable=False)
    fileid = Column(String, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="requests")
    # queue_request: Mapped["Queue"] = relationship("Queue", back_populates="request")

    def get_status_text(self):
        if not self.finished:

            if self.user.langenum == LangEnum.russian:

                return f"""
📁 Имя файла : {self.filename}
💿 Размер файла : {get_file_size(self.filesize)}
            
▶️ VirusTotal сканирует файл {self.filename}. Пожалуйста подождите."""

            else:
                return f"""
📁 File name : {self.filename}
💿 File size : {get_file_size(self.filesize)}
            
▶️ VirusTotal is scanning {self.filename}. Please wait."""


class LinkRequest(BaseRequest):
    __tablename__ = "linkrequests"
    id = Column(Integer, primary_key=True)
    linkchecked = Column(String)

    user: Mapped["User"] = relationship("User", back_populates="linkrequests")
    # linkqueue_request: Mapped["LinkQueue"] = relationship(
    #     "LinkQueue", back_populates="linkrequest"
    # )

    def get_status_text(self):
        if not self.finished:

            if self.user.langenum == LangEnum.russian:

                return f"""
📁 Ссылка : {self.linkchecked}
            
▶️ VirusTotal сканирует ссылку {self.linkchecked}. Пожалуйста подождите."""
            else:
                return f"""
📁 Link : {self.linkchecked}
            
▶️ VirusTotal is scanning {self.linkchecked}. Please wait."""


# class Queue(Base):
#     __tablename__ = "queue"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     request_id = Column(Integer, ForeignKey("requests.id"))
#     position = Column(Integer, nullable=False)

#     user: Mapped["User"] = relationship("User", back_populates="queue_requests")
#     request: Mapped["Request"] = relationship("Request", back_populates="queue_request")


# class LinkQueue(Base):
#     __tablename__ = "linkqueue"
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     linkrequest_id = Column(Integer, ForeignKey("linkrequests.id"))
#     position = Column(Integer, nullable=False)

#     user: Mapped["User"] = relationship("User", back_populates="linkqueue_requests")
#     linkrequest: Mapped["LinkRequest"] = relationship(
#         "LinkRequest", back_populates="linkqueue_request"
#     )


# Create the tables if they don't exist
# Base.metadata.create_all(engine)


def get_or_create_user(telegram_id):
    user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        session.add(user)
        session.commit()
    return user


def get_request_by_id(id: int):
    request = session.query(Request).filter_by(id=id).first()
    if not request:
        return None
    else:
        return request


@router.callback_query(LangCB.filter())
async def language_callback(
    callback_query: types.CallbackQuery, callback_data: LangCB, bot: Bot
):
    print("lang cb")
    user: User = get_or_create_user(callback_query.from_user.id)
    user.langenum = LangEnum(callback_data.language)
    session.add(user)
    session.commit()
    user: User = get_or_create_user(callback_query.from_user.id)

    # await callback_query.message.edit_text('ne twtwtdshgsdfhjsdf')
    await callback_query.message.edit_reply_markup(
        reply_markup=get_language_keyboard(user.langenum.value)
    )


# ! Cancel file check button
@router.callback_query(CancelCB.filter())
async def cancel_check(
    callback_query: types.CallbackQuery, callback_data: CancelCB, bot: Bot
):

    req = get_request_by_id(callback_data.req_id)
    logging.info(f"Request found {req}")

    # get user by telegram id
    if not req:
        user = get_or_create_user(callback_query.from_user.id)

        await callback_query.message.edit_text(
            FileDialogText.get_cancel_check_text(user.langenum)
        )
        return

    await callback_query.message.edit_text(
        FileDialogText.get_cancel_check_text(req.user.langenum, req.filename)
    )

    session.delete(req)
    session.commit()


class AntiVirusClass:

    @staticmethod
    async def get_check_data_from_url(session: aiohttp.ClientSession, url):
        headers = {
            "accept": "application/json",
            "x-apikey": API_KEY,
        }
        text_with_results = json.loads(
            await (await session.get(url, headers=headers)).text()
        )

        return text_with_results

    @staticmethod
    def clear_emojies(
        entities: list[types.MessageEntity], emojies: list, message: types.Message
    ):
        list_links = []

        for entity in entities:
            # Check if entity is a link
            if entity.type == "url":
                # Count the emoju
                offset = entity.offset
                length = entity.length
                i = 0
                for emoj in emojies:
                    if emoj["match_start"] <= entity.offset:
                        offset -= 1
                    if (
                        emoj["match_start"] > entity.offset
                        and emoj["match_start"] < entity.offset + entity.length
                    ):
                        length -= 2

                adress = message.text[offset : offset + length]
                lower_adress = adress.lower()

                list_links.append(lower_adress)

        return list_links

    @classmethod
    async def send_temp_messages(cls, message: types.Message, request: Request):
        """Message to send a status message (and warning message if limit is exceeded)"""

        user = get_or_create_user(message.from_user.id)

        # # Check if the user has reached the daily limit for file requests
        if len(user.requests_today) >= MAX_FILES_PER_DAY:
            await message.answer(
                FileDialogText.get_limit_req_text(
                    user.langenum, MAX_FILES_PER_DAY, CheckTypeEnum.file
                ),
            )
            raise ValueError(
                f"Limit of the checks : {MAX_FILES_PER_DAY} check per day -  exceeded"
            )

        # # send message with status
        id = request.id
        logging.info(f"Request id {id}")

        status_message = await message.bot.send_message(
            chat_id=user.telegram_id,
            text=request.get_status_text(),
            reply_markup=get_cancel_keyboard(
                request.id, request.filename, user.langenum
            ),
            reply_to_message_id=message.message_id,
        )
        request.replyid = status_message.message_id
        session.merge(request)
        session.commit()
        return request, status_message

    # @classmethod
    # def create_queue(cls, request: Request):
    #     last_position = session.query(func.max(Queue.position)).scalar()

    #     if last_position:
    #         queue_position = Queue(request=request, position=last_position + 1)
    #     else:
    #         queue_position = Queue(request=request, position=1)

    #     return queue_position

    def deal_with_text_response(
        text_with_results, request: BaseRequest, isFile: bool = True
    ):
        if not text_with_results["data"]["attributes"]["stats"]:
            return False

        print("Start text_with_results stats")
        stats = text_with_results["data"]["attributes"]["stats"]

        # * determine the number of dangerous files
        dangerous_files = 0
        if stats["suspicious"] != 0 or stats["malicious"] != 0:
            dangerous_files = stats["suspicious"] + stats["malicious"]

        num_of_checks: int = stats["undetected"] + stats["harmless"]

        # * make link

        if isFile:
            hash = text_with_results["meta"]["file_info"]["sha256"]
            suburl = "file"
        else:
            hash = text_with_results["meta"]["url_info"]["id"]
            suburl = "url"

        link = f"https://www.virustotal.com/gui/{suburl}/{hash}/detection"

        if isFile:
            result_text = FileDialogText.get_result_file_text(
                request.user.langenum,
                dangerous_files,
                num_of_checks,
                request.filename,
                get_file_size(request.filesize),
                link,
            )

        else:
            domain = urlparse(request.linkchecked).netloc
            result_text = FileDialogText.get_result_link_text(
                request.user.langenum,
                dangerous_files,
                num_of_checks,
                request.linkchecked,
                link,
                domain,
            )

        request.link = link
        request.result = True
        request = session.merge(request)
        session.commit()

        return result_text

    @staticmethod
    async def send_results_as_message(
        message: types.Message,
        request: Request | LinkRequest,
        result_text: str,
        markup_result: types.InlineKeyboardMarkup,
    ):

        if isinstance(request, Request):
            await message.bot.send_document(
                chat_id=request.user.telegram_id,
                document=request.fileid,
                caption=result_text,
                reply_markup=markup_result,
                reply_to_message_id=request.messageid,
            )
        else:
            await message.bot.send_message(
                chat_id=request.user.telegram_id,
                text=result_text,
                reply_markup=markup_result,
                reply_to_message_id=request.messageid,
            )

        try:
            await message.bot.delete_message(
                chat_id=request.user.telegram_id, message_id=request.replyid
            )
        except TelegramBadRequest as e:
            print("Message cant be deleted")

            # # if isFile:
            # try:

            #     await message.bot.send_document(
            #         chat_id=request.user.telegram_id,
            #         document=request.fileid,
            #         caption=result_text,
            #         reply_markup=markup_result,
            #         reply_to_message_id=request.messageid,
            #     )
            # except TelegramBadRequest as e:
            #     print("inside except")
            #     await message.bot.send_document(
            #         chat_id=request.user.telegram_id,
            #         document=request.fileid,
            #         caption=result_text,
            #         reply_markup=markup_result,
            #     )

    @classmethod
    async def virustotal_response_link_handler(
        cls,
        response: aiohttp.ClientResponse,
        aiosession: aiohttp.ClientSession,
        linkrequest: LinkRequest,
        message: types.Message,
    ):

        # if response is succesfull
        if response.status == 200:
            response_text = await response.text()
            resp_array = json.loads(response_text)

            session.refresh(linkrequest)
            linkrequest.virustotalid = resp_array["data"]["id"]

            # merge request with virustotalid
            linkrequest = session.merge(linkrequest)
            session.commit()

            # use check_link to get data from virustotal
            check_link = resp_array["data"]["links"]["self"]
            text_with_results = await AntiVirusClass.get_check_data_from_url(
                aiosession, check_link
            )

            # get status
            status = text_with_results["data"]["attributes"]["status"]
            logging.info(f"status {status} (first) for link {linkrequest.linkchecked}")

            # if status is not completed and request still exist (cancel button isnt pushed)- go into a loop untill it is
            while (
                not status == "completed" and linkrequest and linkrequest.attempts < 20
            ):
                logging.info(f"status {status} for link {linkrequest.linkchecked}")

                # nimate text by dots, so user will see a request is on
                text = message.text

                # tell how many dots in the end of the message
                dots = text.count(".", len(text) - 3, len(text))
                logging.info(f"dots {dots}")
                logging.info(f"text {text}")
                if dots == 3:
                    text = text[: len(text) - 3]
                else:
                    text += "."

                # animation effect here
                markup = message.reply_markup
                message = await message.edit_text(text, reply_markup=markup)

                # wait for 5 seconds to not to make requests too often
                await asyncio.sleep(5)

                # try to request again and get out from the loop
                text_with_results = await AntiVirusClass.get_check_data_from_url(
                    aiosession, check_link
                )
                status = text_with_results["data"]["attributes"]["status"]

                # add 1 attempt to the request
                linkrequest.attempts += 1

                session.refresh(linkrequest)

            if linkrequest.attempts >= 20:
                logging.error(
                    f"Request to check link {linkrequest.linkchecked} is deleted because of 20 attempts"
                )
                await message.answer(
                    FileDialogText.get_error_analizing_text(
                        linkrequest.user.langenum,
                        linkrequest.linkchecked,
                        CheckTypeEnum.link,
                    ),
                )
                return

            # if completed - return response as text
            return text_with_results

        else:
            logging.info(f"response.status {response.status}")

            await message.bot.send_message(
                linkrequest.user.telegram_id,
                FileDialogText.get_error_analizing_text(
                    linkrequest.user.langenum, linkrequest.filename, CheckTypeEnum.file
                ),
            )

    @classmethod
    async def virustotal_response_handler(
        cls,
        response: aiohttp.ClientResponse,
        aiosession: aiohttp.ClientSession,
        request: Request,
        message: types.Message,
    ):

        # if response is succesfull
        if response.status == 200:
            response_text = await response.text()
            resp_array = json.loads(response_text)
            # get virustotal id - will be used to request results periodically

            session.refresh(request)
            request.virustotalid = resp_array["data"]["id"]

            # merge request with virustotalid
            request = session.merge(request)
            session.commit()

            # use check_link to get data from virustotal
            check_link = resp_array["data"]["links"]["self"]
            text_with_results = await AntiVirusClass.get_check_data_from_url(
                aiosession, check_link
            )

            # get status
            status = text_with_results["data"]["attributes"]["status"]
            logging.info(f"status {status} (first) for file {request.filename}")

            # if status is not completed and request still exist (cancel button isnt pushed)- go into a loop untill it is
            while not status == "completed" and request and request.attempts < 20:
                logging.info(f"status {status} for file {request.filename}")

                # nimate text by dots, so user will see a request is on
                text = message.text

                # tell how many dots in the end of the message
                dots = text.count(".", len(text) - 3, len(text))
                logging.info(f"dots {dots}")
                logging.info(f"text {text}")
                if dots == 3:
                    text = text[: len(text) - 3]
                else:
                    text += "."

                # animation effect here
                markup = message.reply_markup
                message = await message.edit_text(text, reply_markup=markup)

                # wait for 5 seconds to not to make requests too often
                await asyncio.sleep(5)

                # try to request again and get out from the loop
                text_with_results = await AntiVirusClass.get_check_data_from_url(
                    aiosession, check_link
                )
                status = text_with_results["data"]["attributes"]["status"]

                # add 1 attempt to the request
                request.attempts += 1

                # check if request still exist
                session.refresh(request)

            if request.attempts >= 20:
                logging.error(
                    f"Request to check file {request.filename} is deleted because of 20 attempts"
                )
                await message.answer(
                    FileDialogText.get_error_analizing_text(
                        request.user.langenum, request.filename, CheckTypeEnum.file
                    ),
                )
                return

            # if completed - return response as text
            return text_with_results

        else:
            logging.info(f"response.status {response.status}")

            await message.bot.send_message(
                request.user.telegram_id,
                FileDialogText.get_error_analizing_text(
                    request.user.langenum, request.filename, CheckTypeEnum.file
                ),
            )

    @staticmethod
    async def check_links_limit(user: User, message: types.Message):
        # Check if the user has reached the daily limit for file requests
        if len(user.requests_today) >= MAX_LINKS_PER_DAY:
            await message.answer(
                FileDialogText.get_limit_req_text(
                    user.langenum, MAX_LINKS_PER_DAY, CheckTypeEnum.link
                ),
            )
            return False
        return True

    @classmethod
    async def send_file_to_virusportal(cls, message: types.Message, request: Request):
        url = "https://www.virustotal.com/api/v3/files"
        headers = {
            "accept": "application/json",
            "x-apikey": API_KEY,
        }

        async with aiohttp.ClientSession() as aiosession:
            filename = str(request.filename)
            data = aiohttp.FormData()
            file_from_telegram = await message.bot.download(request.fileid)
            data.add_field("file", file_from_telegram, filename=filename)
            logging.info(f"Sending the file {filename} to VirusTotal")
            response = await aiosession.post(url, headers=headers, data=data)

            # go into the loop untill virustotal return a response
            try:
                text_with_results = await cls.virustotal_response_handler(
                    response, aiosession, request, message
                )
            except InvalidRequestError as e:
                # check if the request is  not persistent within this Session

                if not session.query(Request).get(request.id):
                    logging.error(
                        f"Request to check file {filename} is deleted because of the user canceled it"
                    )
                else:
                    raise e

                return

            if text_with_results:
                # return a readable text out from a succesfull response from virustotal
                result_text = cls.deal_with_text_response(text_with_results, request)

                if result_text:
                    # making a markup and send text
                    markup_result = get_results_keyboard(
                        request.link, request.user.langenum
                    )
                    await cls.send_results_as_message(
                        message, request, result_text, markup_result
                    )

    @classmethod
    async def send_link_to_virusportal(
        cls, message: types.Message, linkrequest: LinkRequest
    ):
        url = "https://www.virustotal.com/api/v3/urls"
        headers = {
            "accept": "application/json",
            "x-apikey": API_KEY,
        }

        async with aiohttp.ClientSession() as aiosession:
            logging.info(f"Sending the link to VirusTotal : {linkrequest.linkchecked}")
            data = {"url": linkrequest.linkchecked}

            # getting response from virustotal
            response = await aiosession.post(url, headers=headers, data=data)

            # go into the loop untill virustotal return a response
            try:
                text_with_results = await cls.virustotal_response_link_handler(
                    response, aiosession, linkrequest, message
                )
            except InvalidRequestError as e:
                # check if the request is  not persistent within this Session

                if not session.query(Request).get(linkrequest.id):
                    logging.error(
                        f"Request to check link {linkrequest.linkchecked} is deleted because of the user canceled it"
                    )
                else:
                    raise e

                return

            if text_with_results:

                # return a readable text out from a succesfull response from virustotal
                result_text = cls.deal_with_text_response(
                    text_with_results, linkrequest, isFile=False
                )

                if result_text:
                    # making a markup and send text
                    markup_result = get_results_keyboard(
                        linkrequest.link, linkrequest.user.langenum
                    )
                    await cls.send_results_as_message(
                        message, linkrequest, result_text, markup_result
                    )


# ! check documents
@router.message(F.document)
async def check_file(message: types.Message, bot: Bot, state: FSMContext):

    # create a new user or return already existing one
    user = get_or_create_user(message.from_user.id)

    # if file is more than a 50 mb, return a message
    if message.document.file_size > config.max_size_mb * 1024 * 1024:
        await message.answer(
            FileDialogText.get_big_file_text(
                user.langenum,
                message.document.file_name,
                get_file_size(message.document.file_size),
            )
        )
        return

    # # Create a Request object
    request = Request(
        filename=message.document.file_name,
        filesize=message.document.file_size,
        fileid=message.document.file_id,
        messageid=message.message_id,
        user=user,
    )
    session.add(request)
    session.commit()

    # method responsible for sending a temp message
    request, status_message = await AntiVirusClass.send_temp_messages(message, request)

    # # Wait the minimum delay between requests
    await asyncio.sleep(5)

    # sending file to virusportal
    await AntiVirusClass.send_file_to_virusportal(status_message, request)


# ! check links
@router.message()
async def handle_message(message: types.Message, bot: Bot):

    # Get the user from the database or add a new user if they don't exist
    user = get_or_create_user(message.from_user.id)

    # check for limit and also for any links in message
    is_limit_ok = await AntiVirusClass.check_links_limit(user, message)
    if not is_limit_ok or not message.entities:
        return

    # clear link from any emojies
    list_links = AntiVirusClass.clear_emojies(
        message.entities, emoji_list(message.text), message
    )
    if not list_links:
        return

    # iterate links
    for link in list_links:
        # Create request object
        linkrequest = LinkRequest(
            linkchecked=link, messageid=message.message_id, user=user
        )
        session.add(linkrequest)
        session.commit()

        # send message with status
        status_message = await bot.send_message(
            chat_id=user.telegram_id,
            text=linkrequest.get_status_text(),
            reply_markup=get_cancel_keyboard(linkrequest.id, link, user.langenum),
            reply_to_message_id=message.message_id,
        )

        # remember reply message id
        linkrequest.replyid = status_message.message_id
        session.add(linkrequest)
        session.commit()

        # Wait the minimum delay between requests
        await asyncio.sleep(5)

        # Make a request to the VirusTotal API to analyze the file
        await AntiVirusClass.send_link_to_virusportal(status_message, linkrequest)

        # url = "https://www.virustotal.com/api/v3/urls"
        # headers = {
        #     "accept": "application/json",
        #     "x-apikey": API_KEY,
        # }

        # async with aiohttp.ClientSession() as aiosession:
        #     data = {"url": link}
        #     response = await aiosession.post(url, headers=headers, data=data)

        #     # Handle the response from the VirusTotal API
        #     if response.status == 200:
        #         response_text = await response.text()
        #         linkquere_id = json.loads(response_text)["data"]["id"]
        #         linkqueue_position.linkrequest.virustotalid = linkquere_id
        #         session.add(linkqueue_position.linkrequest)
        #         # await file_states.put((file_id, file_name,file_size, message_id, chat_id, quere_id, 1))

        #     else:
        #         user = get_or_create_user(message.from_user.id)
        #         lang = user.langenum
        #         await bot.send_message(
        #             chat_id,
        #             FileDialogText.get_error_analizing_text(
        #                 lang, link, CheckTypeEnum.link
        #             ),
        #         )

        #     session.commit()


def get_file_size(file_size: int) -> str:
    """
    Convert the input file size (in bytes) to a human-readable string,
    expressed in KB, MB, or GB, depending on the size.

    Args:
        file_size (int): The file size in bytes.

    Returns:
        str: The human-readable file size as a string.
    """
    # Define the units of measure
    units = ["B", "KB", "MB", "GB"]
    # Determine the appropriate unit of measure
    unit_index = 0
    while file_size >= 1024 and unit_index < len(units) - 1:
        file_size /= 1024.0
        unit_index += 1
    # Format the output string
    size_str = "{:.2f} {}".format(file_size, units[unit_index])
    return size_str
