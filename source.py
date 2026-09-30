import requests
import os
import time
from base64 import b64encode
from dataclasses import dataclass

@dataclass
class Song:
    rank: int
    isrc: str | None = None
    title: str | None = None
    artist: str | None = None
    cover_url: str | None = None
    preview_url: str | None = None

    def resolve(self):
        assert self.isrc
        req = requests.get(f'https://api.deezer.com/track/isrc:{self.isrc}')
        req.raise_for_status()
        data = req.json()
        self.title = data['title']
        self.artist = data['artist']['name']
        self.cover_url = data['album']['cover_big']
        self.preview_url = data['preview']

spotify_token_header = None
spotify_token_expire = 0

def get_spotify_token_header():
    global spotify_token_header, spotify_token_expire
    if spotify_token_header is None or spotify_token_expire <= time.time():
        token = b64encode(f'{os.environ['SPOTIFY_CLIENT_ID']}:{os.environ['SPOTIFY_CLIENT_SECRET']}'.encode())
        req = requests.post('https://accounts.spotify.com/api/token?grant_type=client_credentials', headers={
            'Authorization': f'Basic {token.decode()}',
            'Content-Type': 'application/x-www-form-urlencoded',
        })
        req.raise_for_status()
        data = req.json()
        spotify_token_expire = time.time() + data['expires_in']
        spotify_token_header = {
            'Authorization': f'{data['token_type']} {data['access_token']}'
        }
        print(spotify_token_header)
    return spotify_token_header

def get(url: str) -> (str, list[Song]):
    url_parts = url.split('/')

    if 'deezer.com' in url:
        if 'playlist' in url_parts:
            playlist_id = int(url_parts[-1])
            req = requests.get(f'https://api.deezer.com/playlist/{playlist_id}')
            req.raise_for_status()
            data = req.json()
            assert 'error' not in data, f'Could not get playlist: {data['error']['message']}'
            tracks = [
                Song(
                    title=t['title'],
                    artist=t['artist']['name'],
                    cover_url=t['album']['cover_big'],
                    preview_url=t['preview'],
                    rank=t['rank'],
                    isrc=t['isrc']
                ) for t in data['tracks']['data'] if t['preview'] != ''
            ]
            print(f'got {len(tracks)} tracks for deezer playlist {playlist_id} {data['title']}')
            return data['title'], tracks

        elif 'artist' in url_parts:
            artist_id = int(url_parts[-1])
            req = requests.get(f'https://api.deezer.com/artist/{artist_id}')
            req.raise_for_status()
            artist_name = req.json()['name']


            req = requests.get(f'https://api.deezer.com/artist/{artist_id}/top?limit=200')
            req.raise_for_status()
            data = req.json()
            assert 'error' not in data, f'Could not get artist songs: {data['error']['message']}'
            tracks = [
                Song(
                    title=t['title'],
                    artist=t['artist']['name'],
                    cover_url=t['album']['cover_big'],
                    preview_url=t['preview'],
                    rank=t['rank']
                ) for t in data['data'] if t['preview'] != ''
            ]
            tracks_ids = [t['id'] for t in data['data'] if t['preview'] != '']

            if len(tracks) < 15:
                print(f'got only {len(tracks)} for artist {artist_id} {artist_name}, searching for more')
                req = requests.get(f'https://api.deezer.com/search/track?q={artist_name}&limit=50')
                req.raise_for_status()
                data = req.json()
                assert 'error' not in data, f'Could not get artist songs: {data['error']['message']}'
                tracks.extend([
                    Song(
                        title=t['title'],
                        artist=t['artist']['name'],
                        cover_url=t['album']['cover_big'],
                        preview_url=t['preview'],
                        rank=t['rank']
                    ) for t in data['data'] if t['preview'] != '' and t['id'] not in tracks_ids and t['artist']['id'] == artist_id
                ])

            print(f'got {len(tracks)} tracks for deezer artist {artist_id} {artist_name}')
            return artist_name, tracks

        elif 'album' in url_parts:
            album_id = int(url_parts[-1])
            req = requests.get(f'https://api.deezer.com/album/{album_id}')
            req.raise_for_status()
            data = req.json()
            assert 'error' not in data, f'Could not get album: {data['error']['message']}'
            tracks = [
                Song(
                    title=t['title'],
                    artist=t['artist']['name'],
                    cover_url=t['album']['cover_big'],
                    preview_url=t['preview'],
                    rank=t['rank']
                ) for t in data['tracks']['data'] if t['preview'] != ''
            ]
            print(f'got {len(tracks)} tracks for deezer album {album_id}')
            return data['title'], tracks
        
        elif 'link.deezer.com' in url:
            req = requests.get(url)
            req.raise_for_status()
            url = req.history[-1].url.split('?')[0]
            return get(url)
        else:
            raise Exception('Invalid Deezer link')

    elif 'spotify.com' in url:
        if 'playlist' in url_parts:
            tracks = []
            req = requests.get(
                f'https://api.spotify.com/v1/playlists/{url_parts[-1]}?fields=name',
                headers=get_spotify_token_header()
            )
            req.raise_for_status()
            playlist_name = req.json()['name']
            for i in range(0,4):
                print(f'fetching 50 songs from playlist {url_parts[-1]}, {len(tracks)}')
                req = requests.get(
                    f'https://api.spotify.com/v1/playlists/{url_parts[-1]}/items?limit=50&offset={i*50}&fields=total,items(track(popularity,external_ids))',
                    headers=get_spotify_token_header()
                )
                req.raise_for_status()
                for track in req.json()['items']:
                    tracks.append(Song(
                        isrc=track['track']['external_ids']['isrc'],
                        rank=track['track']['popularity']
                    ))
                if len(tracks) >= req.json()['total']:
                    break
            return playlist_name, tracks
        else:
            raise Exception('Invalid Spotify link')
