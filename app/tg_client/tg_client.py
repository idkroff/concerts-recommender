import logging
import os
import re

from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import asyncio

from app.artistsgetter.artists_getter import ArtistsGetter
from app.concertsgetter.concerts_getter import *
from app.gptenricher.enricher import GPTEnricher

TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")

logging.basicConfig(level=logging.INFO)

if not TG_BOT_TOKEN:
    raise ValueError("TG_BOT_TOKEN не задан!")

bot = Bot(token=TG_BOT_TOKEN)

dp = Dispatcher()


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


@dp.message()
async def process_playlist_link(message: Message):
    """
    Обработка текстовых сообщений, содержащих ссылку на плейлист.
    """

    link = None
    user_input = message.text.strip()

    match = re.search(r'(https?://music\.yandex\.ru/.*)', user_input)

    if match:
        link = match.group(1)
        user_input = user_input.replace(link, "").strip()

    if "music.yandex.ru" not in link:
        await message.reply(
            "Ой! 😬 Похоже, что с твоей ссылкой что-то не так. Убедись, что это действительная ссылка на плейлист и попробуй снова."
        )
        return

    await message.reply("Получено! 📝 Просматриваем твой плейлист...")

    try:
        ag = ArtistsGetter(os.getenv("YANDEX_MUSIC_TOKEN"))
        artists = ag.get_artists_from_playlist_by_url(
            playlist_url=link)

        if not artists:
            await message.reply(
                "К сожалению, я не нашёл ни одного исполнителя в твоём плейлисте. 😔 Попробуй отправить ссылку на другой плейлист."
            )
            return

        await message.reply("Ищу концерты исполнителей из твоего плейлиста... 🎤")

        obj = ConcertsGetter(artists)
        concerts = await obj.extract_concerts()

        if concerts:
            distribution = {
                artist.name: artist.distribution for artist in artists}

            enricher = GPTEnricher()
            # user_input = "Список концертов из моего плейлиста"
            enriched_output = enricher.enrich(
                user_input=user_input,
                concerts=concerts,
                distribution=distribution
            )
            await message.reply("Вот что мы нашли:\n\n" + enriched_output)
        else:
            await message.reply("К сожалению, я не нашёл концертов для исполнителей из плейлиста. 😔")

    except Exception as e:
        logging.error(f"Error processing playlist link: {e}")
        await message.reply("Произошла ошибка при обработке твоего плейлиста. Попробуй ещё раз позже.")


async def main():
    """
    Основная функция для запуска диспетчера.
    """
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка запуска бота: {e}")
