import logging
import os
import unittest
from unittest.mock import patch, MagicMock
from artists_getter import ArtistsGetter, Artist


logger = logging.getLogger(__name__)


def test_get_artists_from_playlist():
    ag = ArtistsGetter(os.getenv("YANDEX_MUSIC_TOKEN"))
    artists = ag.get_artists_from_playlist_by_url(playlist_url="https://music.yandex.ru/users/fnikulenko/playlists/1007")

    expected_return_list = [
            Artist(name="GONE.Fludd", distibution=0.38),
            Artist(name="MAYOT", distibution=0.25),
            Artist(name="SHAMAN", distibution=0.12),
            Artist(name="ЛСП", distibution=0.12),
            Artist(name="Люся Чеботина", distibution=0.12),
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
