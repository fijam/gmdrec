"""Talking to the music player over the REST API provided by beefweb.

API spec at https://hyperblast.org/beefweb/api/
"""
import datetime
import time
import logging

import requests
from requests.exceptions import Timeout

SERVER_URL = 'http://127.0.0.1:8880'


def check_connection():
    try:
        requests.get(SERVER_URL, timeout=0.2)
    except Timeout:
        logging.critical("Connection timed out. Make sure Foobar is running and the beefweb plugin is installed.")
        raise()


def request_playlist_content(args):
    t_list = []
    total_time = 0
    response_playlist = requests.get(f'{SERVER_URL}/api/playlists')
    playlist_list = response_playlist.json()['playlists']
    for dictionary in playlist_list:
        if dictionary['isCurrent']:
            global playlist_id  # cop-out
            playlist_id = dictionary['id']
            item_count = dictionary['itemCount']

    payload = {'playlists': 'false', 'playlistItems': 'true',
               'plref': playlist_id, 'plrange': f'0:{item_count}',
               'plcolumns': args.label+', %length_seconds%'}
    response = requests.get(f'{SERVER_URL}/api/query', params=payload)

    for i in range(item_count):
        track_name = response.json()['playlistItems']['items'][i]['columns'][0]
        t_list.append(track_name)
        track_duration = response.json()['playlistItems']['items'][i]['columns'][1].strip()
        if track_duration.isdecimal():
            total_time += int(track_duration)
    print(f'Total playlist duration: {datetime.timedelta(seconds=total_time)}')
    if total_time >= 4800:
        logging.warning('playlist duration exceeds 80 minutes!')
    if item_count > 254:
        logging.warning('cannot record more than 254 tracks!')
    # return a list of tracks to label and total time
    return t_list


def request_track_time():
    response = requests.get(f'{SERVER_URL}/api/player')
    duration = response.json()['player']['activeItem']['duration']
    position = response.json()['player']['activeItem']['position']
    # return remaining time in track (seconds)
    return duration - position


def set_player(command):
    if command == 'mode_play':
        # unmute, no shuffle
        requests.post(f'{SERVER_URL}/api/player', params={'isMuted': 'false', 'playbackMode': '0'})
        requests.post(f'{SERVER_URL}/api/player/play/{playlist_id}/0')  # start from the top
    else:
        requests.post(f'{SERVER_URL}/api/player/{command}')  # play, pause, stop


def insert_2s():
    set_player('pause')
    time.sleep(2.1)
    set_player('play')
