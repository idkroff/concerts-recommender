from dataclasses import dataclass, field
from datetime import datetime as dt
from dataclasses import asdict
from yandex_music import Client
from yandex_music.exceptions import NotFoundError


@dataclass
class Artist:
    """
    Класс артиста 
    """
    name: str = ""
    distribution: float = 0.0

    def __str__(self) -> str:
        """
        Строковое представление артиста
        """
        return f"Артист {self.name} с частотой упоминания {self.distribution}"
    
    def __eq__(self, other) -> bool:
        """
        Компанатор для артистов
        """
        return self.name == other.name and abs(self.distribution - other.distribution) <= 0.02


@dataclass
class Concert:
    artist: Artist = field(default_factory=Artist)
    city: str = ""
    place: str = ""
    datetime: dt = field(default_factory=dt.now)
    price_start: int = 0

    def to_dict(self):
        return {
            "artist": asdict(self.artist),
            "place": self.city + " " + self.place,
            "datetime": self.datetime.strftime("%d %B %Y, %H:%M"),
            "price_start": self.price_start,
        }
