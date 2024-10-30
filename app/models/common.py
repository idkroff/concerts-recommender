from dataclasses import dataclass, field
from datetime import datetime as dt


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
