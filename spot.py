import spotipy
import datetime
import time
import sys
import os
from spotipy.oauth2 import SpotifyOAuth
from unihandecode import Unihandecoder
from settings import URI, client_id, client_secret

if client_id is None:
    print('You need to first add your Spotify developer credentials in settings.conf')
    sys.exit()

scope = "user-read-playback-state,user-modify-playback-state"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri="http://localhost:8080",
                                               scope=scope,
                                               cache_path=f"{os.environ['LOCALAPPDATA']}\gmdrec.cache"))
# windows-specific cache location not commited to git


def asciify(script, args):
    if args.lang_code is None:
        return Unihandecoder().decode(script)
    return Unihandecoder(lang=args.lang_code.casefold()).decode(script)


def check_connection():
    sp.me()


def request_playlist_content(args):
    t_list = []
    total_time = 0
    response = sp.playlist_items(URI,
                                 offset=0,
                                 fields='items.track.name,items.track.artists.name, items.track.duration_ms, total',
                                 additional_types=['track'])
    item_count = (response['total'])

    for i in range(item_count):
        ascii_track_name = asciify(response['items'][i]['track']['artists'][0]['name'] +
                                   ' - ' +
                                   response['items'][i]['track']['name'], args)
        print(ascii_track_name)
        t_list.append(ascii_track_name)
        total_time += round((response['items'][i]['track']['duration_ms'])/1000)
    print(f'Total playlist duration: {datetime.timedelta(seconds=total_time)}')
    if total_time >= 4800:
        print('Warning: duration exceeds 80 minutes!')
    if item_count > 254:
        print('Warning: cannot record more than 254 tracks!')
    # return a list of tracks to label
    return t_list


def request_track_time():
    response = sp.currently_playing()
    duration = (response['item']['duration_ms'])
    position = (response['progress_ms'])
    return round((duration - position)/1000)


def set_player(command):
    if command == 'mode_play':
        # no shuffle, start from the top
        sp.shuffle(state=False)
        sp.start_playback(context_uri=URI, offset={"position": 0})
    if command == 'play':
        sp.start_playback()
    if command in ['stop', 'pause']:
        sp.pause_playback()


def insert_2s():
    set_player('pause')
    time.sleep(2.1)
    set_player('play')
