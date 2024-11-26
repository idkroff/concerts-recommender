import logging
from yandex_music import Client
from typing import Set
from json import loads


logger = logging.getLogger(__name__)


class ArtistsGetter:
    """
    Основной класс модуля
    """
    def __init__(self, token) -> None:
        """
        Конструктор класса: инициализирует объект клиента API через токен
        """
        self.client: Client = Client(token)
        self.client.init()

    def get_chart(self) -> None:
        """
        Метод, выводящий в основной поток вывода мировой чарт 
        """
        chart = self.client.chart("world").chart
        text = [f'🏆 {chart.title}', chart.description, '', 'Треки:']

        for track_short in chart.tracks:
            track, chart = track_short.track, track_short.chart
            artists = ''
            if track.artists:
                artists = ' - ' + ', '.join(artist.name for artist in track.artists)

            track_text = f'{track.title}{artists}'

            if chart.progress == 'down':
                track_text = '🔻 ' + track_text
            elif chart.progress == 'up':
                track_text = '🔺 ' + track_text
            elif chart.progress == 'new':
                track_text = '🆕 ' + track_text
            elif chart.position == 1:
                track_text = '👑 ' + track_text

            track_text = f'{chart.position} {track_text}'
            text.append(track_text)

        print('\n'.join(text))

    def get_artists_from_playlist_by_url(self, playlist_url: str) -> list:
        """
        Метод, принимающий ссылку на плейлист и позвращающий список обнаруженных исполнителей
        """
        #  https://music.yandex.ru/users/fnikulenko/playlists/1006
        parsed_url = playlist_url.split("/")
        playlist_id = parsed_url[-1]
        user_id = parsed_url[-3]

        found_artists: Set[str] = set()
        
        response = self.client.users_playlists(kind=playlist_id, user_id=user_id)
        for track in response.fetch_tracks():
            for artist in track.track.artists:
                found_artists.add(artist.name)

        return list(found_artists)




