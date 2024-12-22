import os
import re

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command

from app.artistsgetter.artists_getter import ArtistsGetter
from app.concertsgetter.concerts_getter import ConcertsGetter
from app.gptenricher.enricher import GPTEnricher
from app.context import set_request_id

import asyncio
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
    global is_active
    is_active = True

    await message.reply(
        "Привет! Я бот, который поможет тебе найти ближайшие концерты исполнителей из твоего плейлиста 🎶\n"
        "Просто отправь мне ссылку на плейлист!\n"
        "Можешь также указать свои пожелания!"
    )


@dp.message(Command("stop"))
async def stop_bot(message: Message):
    """
    Завершение работы бота по команде /stop.
    """

    await message.reply("Завершаю работу... 🛑\nДля возобновления введите /start.")
    global is_active
    is_active = False
    logger.info("Бот завершил работу.")


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
    if not is_active:
        return

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
            await status_message.edit_text("Вот что мы нашли:\n\n" + enriched_output, parse_mode="HTML", disable_web_page_preview=True)
        else:
            await status_message.edit_text("К сожалению, я не нашёл концертов для исполнителей из плейлиста. 😔")
    except Exception as e:
        if "SCRAPER_API_REQUEST_DENIED" in str(e):
            logger.error(f"SCRAPER_API_REQUEST_DENIED: {e}")

            notification_text = (
                "⚠️ Произошла ошибка SCRAPER_API_REQUEST_DENIED:\n"
                f"User ID: {message.from_user.id}\n"
                f"Message ID: {message.message_id}\n"
                f"Link: {link or 'None'}\n"
                f"Error: {str(e)}"
            )
            try:
                NOTIFICATION_USER_ID = os.getenv("NOTIFICATION_USER_ID")
                await message.bot.send_message(
                    chat_id=NOTIFICATION_USER_ID,
                    text=notification_text
                )
            except Exception as notify_error:
                logger.error(f"Не удалось отправить уведомление: {
                             notify_error}")

            await status_message.edit_text(
                "к сожалению, сейчас мы не можем обработать ваш запрос... 😔🎶 Уже работаем над исправлением! ✨"
            )
        else:
            logging.error(f"Error processing playlist link: {e}")
            await status_message.edit_text(f"Произошла ошибка при обработке твоего плейлиста\. Попробуй ещё раз позже\.\n||Request ID: {message.message_id}||", parse_mode="MarkdownV2")


class TGClient:
    def __init__(self):
        TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
        if not TG_BOT_TOKEN:
            raise ValueError("TG_BOT_TOKEN not found in env!")

        self.bot = Bot(token=TG_BOT_TOKEN)
        global is_active
        is_active = True

    async def start(self):
        try:
            await dp.start_polling(self.bot)
        except Exception as e:
            logging.error(f"Ошибка запуска бота: {e}")
