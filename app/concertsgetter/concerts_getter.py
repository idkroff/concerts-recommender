import asyncio
import aiohttp
from bs4 import BeautifulSoup
from transliterate import translit
from app.models.common import Concert, Artist
from datetime import datetime as dt
import json
import os

from typing import List

import logging

logger = logging.getLogger(__name__)


class ConcertsGetter:
    def __init__(self, artists: List[Artist]):
        self.artists: List[Artist] = artists

        self.__scraper_api_token = os.getenv("SCRAPER_API_TOKEN")
        if self.__scraper_api_token is None:
            raise Exception("token not found in env SCRAPER_API_TOKEN")

        self.__q_all_concerts = os.getenv("CONCERTS_GETTER_MAX_CONCERTS_ALL")
        if not (self.__q_all_concerts is None):
            self.__q_all_concerts = int(self.__q_all_concerts)

    async def extract_data_from_url(self, url: str):
        try:
            scraper_url = f"http://api.scraperapi.com?api_key={self.__scraper_api_token}&url={url}"
            async with aiohttp.ClientSession() as session:
                async with session.get(scraper_url) as response:
                    if response.status != 200:
                        raise Exception(f"Not OK request: url = {url}, status = {response.status}")
                    text = await response.text()
                    logger.debug(f"Successful request: url = {url}")
                    return text
        except Exception as e:
            logger.error(str(e))

    async def get_time_for_concert(self, url: str):
        text_html = await self.extract_data_from_url(url)

        soup = BeautifulSoup(text_html, "html.parser")

        hours, minutes = map(int, soup.find("span", class_="session-date__time").text.split(":"))

        return hours, minutes

    async def find_concert_info(self, url: str, artist: Artist):
        text_html = await self.extract_data_from_url(url)

        try:
            soup = BeautifulSoup(text_html, "html.parser")

            concerts: List[Concert] = list()
            all_concerts_divs = soup.findAll("div", class_="person-schedule-item")
            all_concerts_in_json = list(
                json.loads(soup.find("script", type="application/ld+json").string)["performerIn"])
        except Exception as e:
            logger.error(str(e))
            return []

        for i in range(min(len(all_concerts_in_json), len(all_concerts_divs))):
            if len(concerts) >= min(int(artist.distribution * 10), 4):
                break
            if not (self.__q_all_concerts is None):
                if self.__q_all_concerts <= 0:
                    break

            concert_data = all_concerts_in_json[i]
            try:
                concert_info = Concert()

                concert_info.artist = artist

                year, month, day = map(int, concert_data.get("startDate").split("-"))
                ref_for_date = concert_data["url"]
                hours, minutes = await self.get_time_for_concert(ref_for_date)
                concert_info.datetime = dt(year, month, day, hours, minutes)
                if concert_info.datetime < dt.now():
                    continue

                concert_info.city = all_concerts_divs[i].find("div", class_="person-schedule-place__city").text
                concert_info.place = concert_data["location"]["name"]
                concert_info.price_start = int(concert_data["offers"]["price"])

                concerts.append(concert_info)
                if not (self.__q_all_concerts is None):
                    self.__q_all_concerts -= 1
            except Exception:
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

            artist_translit_variants: List[str] = list()
            artist_translit_variants.append(artist_translit)
            artist_translit_variants.append(artist_translit.replace("j", "i"))
            artist_translit_variants.append(artist_translit.replace("i", "j"))
            artist_translit_temp = artist_translit
            for i in range(len(artist_translit)):
                if artist_translit_temp[i] == "j":
                    artist_translit_temp = artist_translit_temp[:i] + "i" + artist_translit_temp[i + 1:]
                elif artist_translit_temp[i] == "i":
                    artist_translit_temp = artist_translit_temp[:i] + "j" + artist_translit_temp[i + 1:]
            artist_translit_variants.append(artist_translit_temp)

            artist_urls_variants: List[str] = [f"https://afisha.yandex.ru/artist/{artist_translit}?city=moscow" for
                                               artist_translit in artist_translit_variants]
            return list(set(artist_urls_variants))
        except Exception as e:
            logger.error(str(e))

    async def extract_concerts(self):
        tasks = [ConcertsGetter.make_url(artist) for artist in self.artists]
        temp_urls = await asyncio.gather(*tasks)
        urls: List[tuple] = list()
        for i in range(len(temp_urls)):
            for url in temp_urls[i]:
                if url is not None:
                    urls.append((url, i))

        tasks = [self.find_concert_info(urls[i][0], self.artists[urls[i][1]]) for i in range(len(urls))]
        results = await asyncio.gather(*tasks)

        concerts_list: List = list()
        for res in results:
            for el in res:
                concerts_list.append(el)

        concerts_list.sort(key=lambda x: x.artist.distribution, reverse=True)

        return concerts_list
