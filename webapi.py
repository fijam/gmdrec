"""Talking to the music player over the REST API provided by beefweb.

API spec at https://hyperblast.org/beefweb/api/

Functions:

    check_connection()
    request_playlist_content(args)
    request_track_time()
    set_player(command)
    insert_2s()
"""
import datetime
import time
import logging

import requests
from requests.exceptions import Timeout

from settings import server_url


def check_connection():
    try:
        requests.get(server_url, timeout=0.2)
    except Timeout:
        logging.critical("Connection timed out. Make sure Foobar is running and the beefsam plugin is installed.")
        raise()


def request_playlist_content(args):
    t_list = []
    total_time = 0
    response_playlist = requests.get(f'{server_url}/api/playlists')
    playlist_list = response_playlist.json()['playlists']
    for dictionary in playlist_list:
        if dictionary['isCurrent']:
            global playlist_id  # cop-out
            playlist_id = dictionary['id']
            item_count = dictionary['itemCount']

    payload = {'playlists': 'false', 'playlistItems': 'true',
               'plref': playlist_id, 'plrange': f'0:{item_count}',
               'plcolumns': args.label+', %length_seconds%'}
    response = requests.get(server_url+'/api/query', params=payload)

    for i in range(item_count):
        track_name = response.json()['playlistItems']['items'][i]['columns'][0]
        t_list.append(track_name)
        total_time += int(response.json()['playlistItems']['items'][i]['columns'][1])
    print(f'Total playlist duration: {datetime.timedelta(seconds=total_time)}')
    if total_time >= 4800:
        logging.warning('playlist duration exceeds 80 minutes!')
    if item_count > 254:
        logging.warning('cannot record more than 254 tracks!')
    # return a list of tracks to label and total time
    return t_list


def request_track_time():
    response = requests.get(f'{server_url}/api/player')
    duration = response.json()['player']['activeItem']['duration']
    position = response.json()['player']['activeItem']['position']
    # return remaining time in track (seconds)
    return duration - position


def set_player(command):
    if command == 'mode_play':
        # unmute, no shuffle
        requests.post(f'{server_url}/api/player', params={'isMuted': 'false', 'playbackMode': '0'})
        requests.post(f'{server_url}/api/player/play/{playlist_id}/0')  # start from the top
    else:
        requests.post(f'{server_url}/api/player/{command}')  # play, pause, stop


def insert_2s():
    set_player('pause')
    time.sleep(2.1)
    set_player('play')
