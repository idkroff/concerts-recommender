import pytest
from unittest.mock import AsyncMock
from aiogram.types import Message
from app.tg_client.tg_client import TGClient
from app.tg_client.tg_client import greet_user, process_playlist_link


@pytest.mark.asyncio
async def test_greet_user():
    """
    Тест команды /start.
    """
    message = AsyncMock(spec=Message)
    message.text = "/start"
    message.reply = AsyncMock()

    await greet_user(message)

    message.reply.assert_called_once_with(
        "Привет! Я бот, который поможет тебе найти ближайшие концерты исполнителей из твоего плейлиста 🎶\n"
        "Просто отправь мне ссылку на плейлист!\n"
        "Можешь также указать свои пожелания!"
    )


@pytest.mark.asyncio
async def test_process_playlist_link_invalid():
    """
    Тест обработки некорректной ссылки на плейлист.
    """
    message = AsyncMock(spec=Message)
    message.text = "Некорректный текст"
    message.message_id = 123
    message.reply = AsyncMock()

    await process_playlist_link(message)

    message.reply.assert_called_once_with(
        "Ой! 😬 Похоже, что с твоей ссылкой что-то не так. Убедись, что это действительная ссылка на плейлист и попробуй снова."
    )
