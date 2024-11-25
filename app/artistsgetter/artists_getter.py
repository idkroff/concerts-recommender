import logging
from yandex_music import Client
from typing import Set


logger = logging.getLogger(__name__)


class ArtistsGetter:
    """
    Основной класс модуля
    """
    def __init__(self) -> None:
        """
        Конструктор класса: инициализирует объект клиента API через токен
        """
        self.client: Client = Client() #  client = Client('token').init()
        self.client.init()
        self.artists: Set[Artist] = set()

class Artist:
    """
    Класс артиста, наполнение которого приходит от YANDEX-API
    """
    


