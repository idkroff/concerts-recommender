import asyncio
import pytest

from .concerts_getter import ConcertsGetter
from app.models.common import Artist


# тесты make_url
@pytest.mark.parametrize("test_value, expected_ans",
                         [("Люся Чеботина", "https://afisha.yandex.ru/artist/liusia-chebotina?city=moscow"),
                          ("GONE.Fludd", "https://afisha.yandex.ru/artist/gone-fludd?city=moscow"),
                          ("Friendly Thug 52 NGG", "https://afisha.yandex.ru/artist/friendly-thug-52-ngg?city=moscow")])
def test_make_url(test_value, expected_ans):
    assert expected_ans in asyncio.run(ConcertsGetter.make_url(Artist(test_value, 0)))
