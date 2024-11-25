import app.context
from .enricher import GPTEnricher
from app.logger import setup_logger
from app.models.common import Concert, Artist
from datetime import datetime as dt
import uuid

import logging
logger = logging.getLogger(__name__)


tests = [
    {
        "concerts": [
            Concert(
                artist=Artist(name="The Rolling Beats"),
                city="Москва",
                place="Олимпийский",
                datetime=dt(2024, 6, 15, 20, 0),
                price_start=1000
            ),
            Concert(
                artist=Artist(name="Pop Diva"),
                city="Санкт-Петербург",
                place="Сибур Арена",
                datetime=dt(2024, 7, 5, 18, 30),
                price_start=750
            ),
            Concert(
                artist=Artist(name="Jazz Ensemble"),
                city="Казань",
                place="Театр им. Г. Камала",
                datetime=dt(2024, 8, 12, 21, 0),
                price_start=600
            )
        ],
        "distribution": {"The Rolling Beats": 0.5, "Pop Diva": 0.3, "Jazz Ensemble": 0.2},
        "user_input": "Интересует выступление в театре или небольшом зале в вечернее время."
    },
    {
        "concerts": [
            Concert(
                artist=Artist(name="Classic Quartet"),
                city="Москва",
                place="Большой театр",
                datetime=dt(2024, 9, 14, 19, 30),
                price_start=5000
            ),
            Concert(
                artist=Artist(name="Rock Legends"),
                city="Казань",
                place="Татнефть Арена",
                datetime=dt(2025, 1, 10, 20, 0),
                price_start=2100
            ),
            Concert(
                artist=Artist(name="Indie Star"),
                city="Санкт-Петербург",
                place="Ледовый дворец",
                datetime=dt(2024, 4, 10, 20, 0),
                price_start=3000
            ),
            Concert(
                artist=Artist(name="Acoustic Vibes"),
                city="Санкт-Петербург",
                place="Сибур Арена",
                datetime=dt(2024, 10, 1, 19, 0),
                price_start=1900
            ),
            Concert(
                artist=Artist(name="EDM Maestro"),
                city="Санкт-Петербург",
                place="Сибур Арена",
                datetime=dt(2024, 11, 22, 22, 0),
                price_start=1200
            ),
        ],
        "distribution": {
            "Indie Star": 0.23,
            "Classic Quartet": 0.16,
            "EDM Maestro": 0.02,
            "Rock Legends": 0.18,
            "Acoustic Vibes": 0.41
        },
        "user_input": "Покажите концерты, которые проходят в Санкт-Петербурге по цене не дороже 2000 рублей."
    },
    {
        "concerts": [
            Concert(
                artist=Artist(name="Classic Quartet"),
                city="Москва",
                place="Большой театр",
                datetime=dt(2024, 9, 14, 19, 30),
                price_start=5000
            ),
            Concert(
                artist=Artist(name="Rock Legends"),
                city="Казань",
                place="Татнефть Арена",
                datetime=dt(2025, 1, 10, 20, 0),
                price_start=2100
            ),
            Concert(
                artist=Artist(name="Indie Star"),
                city="Санкт-Петербург",
                place="Ледовый дворец",
                datetime=dt(2024, 4, 10, 20, 0),
                price_start=3000
            ),
            Concert(
                artist=Artist(name="Acoustic Vibes"),
                city="Санкт-Петербург",
                place="Сибур Арена",
                datetime=dt(2024, 10, 1, 19, 0),
                price_start=1900
            ),
            Concert(
                artist=Artist(name="EDM Maestro"),
                city="Санкт-Петербург",
                place="Сибур Арена",
                datetime=dt(2024, 11, 22, 22, 0),
                price_start=1200
            ),
        ],
        "distribution": {
            "Indie Star": 0.23,
            "Classic Quartet": 0.16,
            "EDM Maestro": 0.02,
            "Rock Legends": 0.18,
            "Acoustic Vibes": 0.41
        },
        "user_input": "в москве"
    }
]


def main():
    setup_logger(logging.DEBUG)
    enricher = GPTEnricher()

    for tt in tests:
        app.context.set_request_id(uuid.uuid4())
        input("\n=====Enter to continue=====\n")

        answer = enricher.enrich(
            tt["user_input"], tt["concerts"], tt["distribution"])
        logger.debug(f"Got answer:\n{answer}\n\n")


if __name__ == "__main__":
    main()
