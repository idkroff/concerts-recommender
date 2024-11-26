import logging

from aiogram import *
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.dispatcher.dispatcher import Dispatcher


from app.artistsgetter.artists_getter import ArtistsGetter
# from app.concerts_getter.concerts_getter import get_concerts
from app.gptenricher.enricher import GPTEnricher

API_TOKEN = "8085801358:AAHQBk89mSGY1hlRwXZXaw-Xy0qrosSlXcw"

logging.basicConfig(level=logging.INFO)


class TelegramClient:
    def __init__(self):
        self.bot = Bot(token=API_TOKEN)
        self.dp = Dispatcher(self.bot)

        self.dp.register_message_handler(self.greet_user, commands=["start"])
        self.dp.register_message_handler(
            self.process_playlist_link, content_types=["text"])

    async def greet_user(self, message: Message):
        await message.reply(
            "Привет! Я бот, который поможет тебе найти ближайшие концерты исполнителей из твоего плейлиста 🎶\n"
            "Просто отправь мне ссылку на плейлист!"
        )

    async def process_playlist_link(self, message: Message):
        link = message.text.strip()
        if "music.yandex.ru" not in link:
            await message.reply(
                "Ой! 😬 Похоже, что с твоей ссылкой что-то не так. Убедись, что это действительная ссылка на плейлист и попробуй снова."
            )
            return

        await message.reply("Получено! 📝 Просматриваем твой плейлист...")

        try:
            artists = get_artists(link)
            if not artists:
                await message.reply(
                    "К сожалению, я не нашёл ни одного исполнителя в твоём плейлисте. 😔 Попробуй отправить ссылку на другой плейлист."
                )
                return

            await message.reply("Ищу концерты исполнителей из твоего плейлиста... 🎤")

            concerts = get_concerts(artists)
            enriched_response = enrich_concerts(
                concerts, user_input=message.text)

            if not enriched_response:
                await message.reply(
                    "К сожалению, я не нашёл ни одного концерта для исполнителей из твоего плейлиста. 😔 Попробуй отправить ссылку на другой плейлист."
                )
                return

            reply = "Я нашёл несколько концертов, которые могут тебя заинтересовать! Вот список:\n"
            for artist, concert_list in enriched_response.items():
                for concert in concert_list:
                    reply += (
                        f"🎶 {artist}\n"
                        f"📅 Дата: {concert['date']}\n"
                        f"📍 Место: {concert['location']}\n\n"
                    )

            await message.reply(reply)

        except Exception as e:
            logging.error(f"Error processing playlist link: {e}")
            await message.reply("Произошла ошибка при обработке твоего плейлиста. Попробуй ещё раз позже.")

    def serve(self):
        executor.start_polling(self.dp, skip_updates=True)
