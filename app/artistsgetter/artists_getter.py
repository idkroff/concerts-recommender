from dataclasses import dataclass, field
from datetime import datetime as dt
from dataclasses import asdict
from yandex_music import Client
from yandex_music.exceptions import NotFoundError

from app.models.common import Artist


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

    def get_artists_from_playlist_by_url(self, playlist_url: str) -> list[Artist]:
        """
        Метод, принимающий ссылку на плейлист и позвращающий список обнаруженных исполнителей
        """
        parsed_url = playlist_url.split("/")
        playlist_id = parsed_url[-1]
        user_id = parsed_url[-3]

        found_artists: dict[str, int] = dict()
        result_artists_list: list[Artist] = list()

        # Padding for cases when more than one artist on a track
        track_count_padding = 0
        
        try: 
            response_tracks = self.client.users_playlists(kind=playlist_id, user_id=user_id).fetch_tracks()
            for track in response_tracks:
                track_count_padding += -1 + len(track.track.artists)

                for artist in track.track.artists:
                    if artist.name in found_artists:
                        found_artists[artist.name] += 1
                    else:
                        found_artists[artist.name] = 1

            for artist_name, artist_distibution in found_artists.items():
                result_artists_list.append(Artist(
                        name = artist_name,
                        distibution = round(artist_distibution / (len(response_tracks) + track_count_padding), 2)
                    )
                )

            return sorted(result_artists_list, key=lambda x: (-x.distribution, x.name))
        
        except NotFoundError as e:
            return f"Плейлист пользователя {user_id} с идентификатором {playlist_id} не найден или не является публичным"
