from dataclasses import dataclass, field
from datetime import datetime as dt
from dataclasses import asdict


@dataclass
class Artist:
    name: str = ""


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
