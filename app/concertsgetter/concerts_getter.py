import asyncio
import aiohttp
from bs4 import BeautifulSoup
from transliterate import translit
from app.models.common import Concert, Artist
from datetime import datetime as dt
import json

from typing import List

import logging

logger = logging.getLogger(__name__)


class ConcertsGetter:
    def __init__(self, artists: List[Artist]):
        self.artists: List[Artist] = artists

    @staticmethod
    async def extract_data_from_url(url: str):
        for i in range(5):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status != 200:
                            raise Exception(f"Not OK request: url = {url}, status = {response.status}, att = {i + 1}")
                        text = await response.text()
                        logger.debug(f"Successful request: url = {url}")
                        return text
            except Exception as e:
                logger.error(str(e))

    @staticmethod
    async def get_time_for_concert(url: str):
        text_html = await ConcertsGetter.extract_data_from_url(url)

        soup = BeautifulSoup(text_html, "html.parser")

        hours, minutes = map(int, soup.find("span", class_="session-date__time").text.split(":"))

        return hours, minutes

    @staticmethod
    async def find_concert_info(url: str, artist: Artist):
        text_html = await ConcertsGetter.extract_data_from_url(url)

        try:
            soup = BeautifulSoup(text_html, "html.parser")

            concerts: List[Concert] = list()
            all_concerts_divs = soup.findAll("div", class_="person-schedule-item person-schedule-list__item")
            all_concerts_in_json = list(
                json.loads(soup.find("script", type="application/ld+json").string)["performerIn"])
        except Exception as e:
            logger.error(str(e))
            return []

        for i in range(min(len(all_concerts_in_json), len(all_concerts_divs))):
            concert_data = all_concerts_in_json[i]
            try:
                concert_info = Concert()

                concert_info.artist = artist

                year, month, day = map(int, concert_data.get("startDate").split("-"))
                ref_for_date = concert_data["url"]
                hours, minutes = await ConcertsGetter.get_time_for_concert(ref_for_date)
                concert_info.datetime = dt(year, month, day, hours, minutes)

                concert_info.city = all_concerts_divs[i].find("div", class_="person-schedule-place__city").text
                concert_info.place = concert_data["location"]["name"]
                concert_info.price_start = int(concert_data["offers"]["price"])

                concerts.append(concert_info)
            except Exception as e:
                logger.warning(str(e))
                logger.warning(f"Can't get info about a {artist.name}'s concert")
        return concerts

    @staticmethod
    async def make_url(artist: Artist):
        try:
            artist_translit = str(translit(artist.name, "ru", reversed=True))
            for i in range(len(artist_translit)):
                if not artist_translit[i].isalnum():
                    artist_translit = artist_translit.replace(artist_translit[i], "-")
            artist_translit = artist_translit.lower()

            return f"https://afisha.yandex.ru/artist/{artist_translit}?city=moscow"
        except Exception as e:
            logger.error(str(e))

    async def extract_concerts(self):
        tasks = [ConcertsGetter.make_url(artist) for artist in self.artists]
        urls = await asyncio.gather(*tasks)
        urls = [url for url in urls if url is not None]

        tasks = [ConcertsGetter.find_concert_info(urls[i], self.artists[i]) for i in range(len(urls))]
        return await asyncio.gather(*tasks)
