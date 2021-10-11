# Talking to the music player and sanitizing data.
import datetime

import requests
from requests.exceptions import Timeout
from unihandecode import Unihandecoder

from settings import *


def asciify(script, args):
    if args.lang_code is None:
        return Unihandecoder().decode(script)
    return Unihandecoder(lang=args.lang_code.casefold()).decode(script)


def check_connection():
    try:
        requests.get(server_url, timeout=0.2)
    except Timeout:
        print("Connection timed out. Make sure Foobar is running and the beefsam plugin is installed.")
        raise()


def request_playlist_info():
    response = requests.get(server_url + '/api/playlists')
    # return playlist ID and number of tracks
    return response.json()['playlists'][0]['id'], response.json()['playlists'][0]['itemCount']


def request_playlist_content(playlist_id, item_count, args):
    t_list = []
    total_time = 0
    payload = {'playlists': 'true', 'playlistItems': 'true',
               'plref': playlist_id, 'plrange': '0:' + str(item_count),
               'plcolumns': args.label+', %length_seconds%'}
    response = requests.get(server_url+'/api/query', params=payload)

    for i in range(item_count):
        ascii_track_name = asciify(response.json()['playlistItems']['items'][i]['columns'][0], args)
        print(ascii_track_name)
        t_list.append(ascii_track_name)
        total_time += int(response.json()['playlistItems']['items'][i]['columns'][1])
    print(f'Total playlist duration: {datetime.timedelta(seconds=total_time)}')
    if total_time >= 4800:
        print('Warning: duration exceeds 80 minutes!')
    if item_count > 254:
        print('Warning: cannot record more than 254 tracks!')
    # return a list of tracks to label and total time
    return t_list, total_time


def request_track_time():
    response = requests.get(server_url + '/api/player')
    duration = response.json()['player']['activeItem']['duration']
    position = response.json()['player']['activeItem']['position']
    # return remaining time in track (seconds)
    return duration - position


def set_mode_play(playlist_id):
    requests.post(server_url + '/api/player', params={'isMuted': 'false', 'playbackMode': '0'})  # unmute, no shuffle
    requests.post(server_url + '/api/player/play/' + playlist_id+'/0')  # start from the top


def set_player(command):
    requests.post(server_url + '/api/player/' + command)  # play, pause, stop