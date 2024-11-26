from artists_getter import ArtistsGetter


ag = ArtistsGetter("y0_AgAAAAB6YHEeAAG8XgAAAAEaCAe4AAA0mVgyVVtB8JeBWADcYz7JcEQPkQ")
artists = ag.get_artists_from_playlist_by_url(playlist_url="https://music.yandex.ru/users/fnikulenko/playlists/1006")
print(artists)