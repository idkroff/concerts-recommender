import logging
import os

from .artists_getter import ArtistsGetter
from app.models.common import Artist


logger = logging.getLogger(__name__)


def test_get_artists_from_playlist():
    ag = ArtistsGetter(os.getenv("YANDEX_MUSIC_TOKEN"))
    artists = ag.get_artists_from_playlist_by_url(
        playlist_url="https://music.yandex.ru/users/fnikulenko/playlists/1007")

    expected_return_list = [
        Artist(name="GONE.Fludd", distribution=0.38),
        Artist(name="MAYOT", distribution=0.25),
        Artist(name="SHAMAN", distribution=0.12),
        Artist(name="ЛСП", distribution=0.12),
        Artist(name="Люся Чеботина", distribution=0.12),
    ]

    try:
        for i in range(len(artists)):
            print(f"{i} real — {artists[i]}")
            print(f"{i} expected — {expected_return_list[i]}", end="\n\n")
            assert artists[i] == expected_return_list[i]
    except Exception as e:
        print(e)


if __name__ == '__main__':
    test_get_artists_from_playlist()
