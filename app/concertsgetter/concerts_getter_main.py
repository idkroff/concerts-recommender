import asyncio

from .concerts_getter import ConcertsGetter
from app.models.common import Artist
from app.logger import setup_logger

import logging

logger = logging.getLogger(__name__)


def main():
    setup_logger(logging.DEBUG)

    names = ["MAYOT", "GONE.Fludd", "Шаман", "Люся Чеботина"]
    artists = [Artist(names[i], (i + 1) / 10) for i in range(len(names))]

    obj = ConcertsGetter()
    ans = asyncio.run(obj.extract_concerts(artists))
    print(f"len(ans) = {len(ans)}")
    print(f"ans: {ans}")


if __name__ == "__main__":
    main()
