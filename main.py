import asyncio
import logging
from app.tg_client.tg_client import TGClient
from app.logger import setup_logger


if __name__ == "__main__":
    setup_logger(level=logging.DEBUG)

    client = TGClient()
    asyncio.run(client.start())
