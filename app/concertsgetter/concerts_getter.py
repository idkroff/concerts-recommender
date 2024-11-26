import asyncio
import aiohttp
from bs4 import BeautifulSoup
from transliterate import translit
from app.models.common import Concert, Artist
from datetime import datetime as dt
import requests
import json

from typing import List

import logging

logger = logging.getLogger(__name__)


class ConcertsGetter:
    def __init__(self, artists: List[Artist]):
        self.artists: List[Artist] = artists

    @staticmethod
    async def extract_data_from_url(session, url: str):
        for i in range(5):
            try:
                async with session.get(url) as response:
                    if response.status != 200:
                        raise Exception(f"Not OK request: url = {url}, status = {response.status}, att = {i}")
                    text = await response.text()
                    logger.debug(f"Successful request: url = {url}")
                    return text
            except Exception as e:
                logger.error(str(e))
                continue

    async def get_time_for_concert(self, session, url: str):
        text_html = await ConcertsGetter.extract_data_from_url(session, url)

        if text_html == "":
            return dt(0, 0, 0, 0, 0)

        soup = BeautifulSoup(text_html, "html.parser")

        hours, minutes = map(int, soup.find("span", class_="session-date__time").text.split(":"))

        return hours, minutes

    async def find_concert_info(self, session, url: str, artist: Artist):
        text_html = await ConcertsGetter.extract_data_from_url(session, url)

        try:
            soup = BeautifulSoup(text_html, "html.parser")

            concerts: List[Concert] = list()
            all_concerts_divs = soup.findAll("div", class_="person-schedule-item person-schedule-list__item")
            all_concerts_in_json = list(json.loads(soup.find("script", type="application/ld+json").string)["performerIn"])
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
                hours, minutes = await self.get_time_for_concert(session, ref_for_date)
                concert_info.datetime = dt(year, month, day, hours, minutes)

                concert_info.city = all_concerts_divs[i].find("div", class_="person-schedule-place__city").text
                concert_info.place = concert_data["location"]["name"]
                concert_info.price_start = int(concert_data["offers"]["price"])

                concerts.append(concert_info)
            except Exception as e:
                logger.warning(str(e))
                logger.warning(f"Can't get info about a {artist.name}'s concert")
                continue
        return concerts

    @staticmethod
    async def make_url(artist: Artist):
        artist_translit = str(translit(artist.name, "ru", reversed=True))
        for i in range(len(artist_translit)):
            if not artist_translit[i].isalpha():
                artist_translit = artist_translit.replace(artist_translit[i], "-")
        artist_translit = artist_translit.lower()

        return f"https://afisha.yandex.ru/artist/{artist_translit}?city=moscow"

    async def extract_concerts(self):
        tasks = [ConcertsGetter.make_url(artist) for artist in self.artists]
        urls = await asyncio.gather(*tasks)
        async with aiohttp.ClientSession() as session:
            tasks = [self.find_concert_info(session, urls[i], self.artists[i]) for i in range(len(urls))]
            return await asyncio.gather(*tasks)


a = Artist()
a.name = "MAYOT"
b = Artist()
b.name = "GONE.Fludd"
c = Artist()
c.name = "шаман"
obj = ConcertsGetter([a, b, c])
ans = asyncio.run(obj.extract_concerts())
for el in ans:
    print(el)
'''

text_html = requests.get("https://afisha.yandex.ru/artist/gone-fludd?city=moscow")
print(text_html.status_code)
soup = BeautifulSoup(text_html.text, "html.parser")
d = soup.find("script", type="application/ld+json").string
d = json.loads(d)
l = list(d["performerIn"])
concerts = []
art = Artist()
art.name = "Gone"
for el in l:
    el = dict(el)
    print(el)
    try:
        conc = Concert()
        conc.artist = art
        conc.price_start = int(el.get("offers").get("price"))
        year, month, day = map(int, el.get("startDate").split("-"))
        conc.place = el.get("location").get("name")

        concerts.append(conc)
    except:
        continue

print(concerts)'''
