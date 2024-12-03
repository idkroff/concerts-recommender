import os
import re

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from app.artistsgetter.artists_getter import ArtistsGetter
from app.concertsgetter.concerts_getter import ConcertsGetter
from app.gptenricher.enricher import GPTEnricher
from app.context import set_request_id

import logging
logger = logging.getLogger(__name__)

dp = Dispatcher()

artists_getter = ArtistsGetter()
concerts_getter = ConcertsGetter()
gpt_enricher = GPTEnricher()


@dp.message(Command("start"))
async def greet_user(message: Message):
    """
    Приветствие пользователя при вводе команды /start.
    """
    await message.reply(
        "Привет! Я бот, который поможет тебе найти ближайшие концерты исполнителей из твоего плейлиста 🎶\n"
        "Просто отправь мне ссылку на плейлист!\n"
        "Можешь также указать свои пожелания!"
    )


@dp.message(Command("reqid"))
async def handle_reqid_command(message: Message):
    """
    Возвращает message_id сообщения, на которое сделан реплай.
    """
    if message.reply_to_message:
        reply_message_id = message.reply_to_message.message_id
        await message.reply(f"ID сообщения, на которое вы ответили: {reply_message_id}")
    else:
        await message.reply("Эта команда должна быть выполнена в ответ на сообщение.")


@dp.message()
async def process_playlist_link(message: Message):
    """
    Обработка текстовых сообщений, содержащих ссылку на плейлист.
    """
    set_request_id(str(message.message_id))
    link = None
    user_input = message.text.strip()

    match = re.search(r'(https?://music\.yandex\.ru/?[^\s]*)', user_input)

    if match:
        link = match.group(1)
        user_input = user_input.replace(link, "").strip()

    if not link or "music.yandex.ru" not in link:
        await message.reply(
            "Ой! 😬 Похоже, что с твоей ссылкой что-то не так. Убедись, что это действительная ссылка на плейлист и попробуй снова."
        )
        return

    status_message = await message.reply("Получено! 📝 Просматриваем твой плейлист...")

    try:
        artists = artists_getter.get_artists_from_playlist_by_url(
            playlist_url=link)

        if not artists:
            await status_message.edit_text(
                "К сожалению, я не нашёл ни одного исполнителя в твоём плейлисте. 😔 Попробуй отправить ссылку на другой плейлист."
            )
            return

        await status_message.edit_text("Ищу концерты исполнителей из твоего плейлиста... 🎤")

        concerts = await concerts_getter.extract_concerts(artists)

        if concerts:
            await status_message.edit_text("Ищу подходящие для тебя варианты... 🔍")
            distribution = {
                artist.name: artist.distribution for artist in artists}

            enriched_output = gpt_enricher.enrich(
                user_input=user_input,
                concerts=concerts,
                distribution=distribution
            )
            await status_message.edit_text("Вот что мы нашли:\n\n" + enriched_output)
        else:
            await status_message.edit_text("К сожалению, я не нашёл концертов для исполнителей из плейлиста. 😔")
    except Exception as e:
        logging.error(f"Error processing playlist link: {e}")
        await status_message.edit_text("Произошла ошибка при обработке твоего плейлиста. Попробуй ещё раз позже.")


class TGClient:
    def __init__(self):
        TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
        if not TG_BOT_TOKEN:
            raise ValueError("TG_BOT_TOKEN not found in env!")

        self.bot = Bot(token=TG_BOT_TOKEN)

    async def start(self):
        try:
            await dp.start_polling(self.bot)
        except Exception as e:
            logging.error(f"Ошибка запуска бота: {e}")
