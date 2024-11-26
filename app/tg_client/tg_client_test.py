import unittest
from unittest.mock import AsyncMock, patch
from app.tg_client.tg_client import TelegramClient


class TestTelegramClient(unittest.TestCase):
    def setUp(self):
        self.tg_client = TelegramClient()

    @patch("app.artists_getter.artists_getter.get_artists", return_value=["Artist 1", "Artist 2"])
    @patch("app.concerts_getter.concerts_getter.get_concerts", return_value={"Artist 1": [{"date": "12 ноября 2024", "location": "Концертный зал 'Звезда'"}]})
    @patch("app.gpt_enricher.enricher.enrich_concerts", return_value={"Artist 1": [{"date": "12 ноября 2024", "location": "Концертный зал 'Звезда'"}]})
    def test_process_playlist_link_valid(self, mock_enrich, mock_get_concerts, mock_get_artists):
        message = AsyncMock()
        message.text = "https://music.yandex.ru/users/music.partners/playlists/2050"
        self.tg_client.process_playlist_link(message)

        mock_get_artists.assert_called_once_with(message.text)
        mock_get_concerts.assert_called_once()
        mock_enrich.assert_called_once()

    @patch("app.artists_getter.artists_getter.get_artists", return_value=[])
    def test_process_playlist_link_no_artists(self, mock_get_artists):
        message = AsyncMock()
        message.text = "https://music.yandex.ru/users/music.partners/playlists/2050"
        self.tg_client.process_playlist_link(message)

        mock_get_artists.assert_called_once_with(message.text)

    def test_process_playlist_link_invalid(self):
        message = AsyncMock()
        message.text = "invalid_link"
        self.tg_client.process_playlist_link(message)

        message.reply.assert_called_with(
            "Ой! 😬 Похоже, что с твоей ссылкой что-то не так. Убедись, что это действительная ссылка на плейлист и попробуй снова."
        )
