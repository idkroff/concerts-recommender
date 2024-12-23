# Телеграм-бот для поиска концертов 🎶

Этот проект представляет собой Телеграм-бота, который помогает пользователю найти ближайшие концерты исполнителей из его плейлиста на Яндекс Музыке. Бот получает ссылку на плейлист, анализирует исполнителей и находит ближайшие концерты через Яндекс Афишу.

## Username телеграм-бота:

Для общения с ботом используйте @ConcertScoutBot.

## Описание

Бот состоит из нескольких компонентов:

1. **artistsGetter** — получает ссылку на плейлист пользователя и возвращает список исполнителей, отсортированных по количеству песен в плейлисте.
2. **concertsGetter** — для каждого исполнителя находит ближайшие концерты с помощью Яндекс Афиши.
3. **gptEnricher** — обогащает данные о концертах, учитывая пожелания пользователя и предпочтения по местоположению.
4. **tgClient** — основной компонент бота, который связывает все части проекта.

## Установка и запуск

1. Клонируйте репозиторий:

    ```bash
    git clone https://github.com/idkroff/concerts-recommender.git
    cd concerts-recommender
    ```

2. Создайте и активируйте виртуальное окружение:

    ```bash
    python -m venv venv
    source venv/bin/activate  # Для Windows: venv\Scripts\activate
    ```

3. Установите зависимости:

    ```bash
    pip install -r app/requirements.txt
    ```

4. Запустите бота:

    ```bash
    python main.py
    ```

## Структура проекта

- **app/artists_getter** — модуль для получения данных о исполнителях из плейлиста.
- **app/concerts_getter** — модуль для получения информации о концертах исполнителей.
- **app/gpt_enricher** — модуль для обогащения данных о концертах с использованием YaGPT.
- **app/tg_client** — модуль для работы с Телеграм-ботом.
- **app/main.py** — точка входа для запуска бота.

## Команды бота

- `/start` — приветственное сообщение от бота.
- Отправьте ссылку на свой плейлист на Яндекс Музыке, и бот начнёт поиск ближайших концертов.

## Пример взаимодействия

1. Пользователь отправляет ссылку на плейлист, также может указать свои пожелания:

    ```
    https://music.yandex.ru/users/music.partners/playlists/2050
    покажи только концерты в декабре

    ```

2. Бот отвечает:

    ```
    Получено! 📝 Просматриваем твой плейлист...
    Ищу концерты исполнителей из твоего плейлиста... 🎤
    Ищу подходящие для тебя варианты... 🔍
    ```

3. Если концерты найдены:

    ```
    Я нашёл несколько концертов, которые могут тебя заинтересовать! Вот список:
    🎶 [Исполнитель 1]
    📅 Дата: 12 ноября 2024
    📍 Место: Концертный зал "Звезда"
    🎶 [Исполнитель 2]
    📅 Дата: 15 ноября 2024
    📍 Место: Дворец спорта
    ```

4. Если концерты не найдены:

    ```
    К сожалению, я не нашёл ни одного концерта для исполнителей из твоего плейлиста. 😔 Попробуй отправить ссылку на другой плейлист.
    ```

## Технологии

- **Яндекс Музыка API** — для получения информации о плейлистах и исполнителях.
- **Яндекс Афиша** — для получения информации о концертах.
- **BeautifulSoup4** и **requests** — для парсинга веб-страниц с концертами.
- **YaGPT** — для обогащения рекомендаций с учётом пожеланий пользователя.
- **aiogram** — для создания Телеграм-бота.
- **Scraper API** — для эффективного парсинга и получения данных с веб-страниц.

## Разработчики

- **Карачурин Михаил** — модуль `concertsGetter`
- **Крупнов Федор** — модуль `gptEnricher` и деплой на Яндекс Cloud
- **Никуленко Филипп** — модуль `artistsGetter`
- **Прудников Михаил** — Телеграм-бот и клиент

