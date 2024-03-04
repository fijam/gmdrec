"""Talking to the music player over the REST API provided by beefweb.

API spec at https://hyperblast.org/beefweb/api/
"""
import datetime
import time
import logging
import sys

import requests
from requests.exceptions import Timeout

SERVER_URL = 'http://127.0.0.1:8880'

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_connection():
    logger.debug("Checking connection to the server...")
    try:
        response = requests.get(SERVER_URL, timeout=0.2)
        logger.debug(f"Server response: {response.status_code}")
    except Timeout:
        logger.critical("Connection timed out. Make sure Foobar/DeadBeeF is running and the beefweb plugin is installed.")
        raise


def request_playlist_content(args):
    t_list = []
    total_time = 0
    logger.debug("Requesting playlist content...")
    response_playlist = requests.get(f'{SERVER_URL}/api/playlists')
    playlist_list = response_playlist.json()['playlists']
    for dictionary in playlist_list:
        if dictionary['isCurrent']:
            global playlist_id  # cop-out
            playlist_id = dictionary['id']
            item_count = dictionary['itemCount']
            logger.debug(f"Current playlist ID: {playlist_id}, Item count: {item_count}")
            break

    payload = {'playlists': 'false', 'playlistItems': 'true',
               'plref': playlist_id, 'plrange': f'0:{item_count}',
               'plcolumns': args.label+', %length_seconds%'}
    logger.debug(f"Query payload: {payload}")
    response = requests.get(f'{SERVER_URL}/api/query', params=payload)

    for i in range(item_count):
        track_name = response.json()['playlistItems']['items'][i]['columns'][0]
        t_list.append(track_name)
        track_duration = response.json()['playlistItems']['items'][i]['columns'][1].strip()
        if track_duration.isdecimal():
            total_time += int(track_duration)
    logger.info(f'Total playlist duration: {datetime.timedelta(seconds=total_time)}')
    # print(f'Total playlist duration: {datetime.timedelta(seconds=total_time)}')
    if total_time >= 4800:
        logging.warning('playlist duration exceeds 80 minutes!')
    if item_count > 254:
        logging.warning('cannot record more than 254 tracks!')
    # return a list of tracks to label and total time
    return t_list


def request_track_time():
    logger.debug("Requesting track time...")
    try:
        response = requests.get(f'{SERVER_URL}/api/player')
        duration = response.json()['player']['activeItem']['duration']
        position = response.json()['player']['activeItem']['position']
        logger.debug(f"Track duration: {duration}, Current position: {position}")
        # return remaining time in track (seconds)
        return duration - position
    except requests.exceptions.RequestException as e:
        logger.error(f"Error requesting track time: {e}")


def set_player(command):
    try:
        logger.debug(f"Setting player with command: {command}")
        if command == 'mode_play':
            # unmute, no shuffle
            unmute_response = requests.post(f'{SERVER_URL}/api/player', params={'isMuted': 'false', 'playbackMode': '0'})
            logger.debug(f"Unmute and set playback mode response - Status code: {unmute_response.status_code}, Body: {unmute_response.text}")
            # Send request to start playback from the top
            play_response = requests.post(f'{SERVER_URL}/api/player/play/{playlist_id}/0')
            logger.debug(f"Start playback from top response - Status code: {play_response.status_code}, Body: {play_response.text}")
        else:
            # Send command to the player (play, pause, stop, etc.)
            response = requests.post(f'{SERVER_URL}/api/player/{command}')
            logger.debug(f"Player command '{command}' response - Status code: {response.status_code}, Body: {response.text}")
	
	    # Check response status for each request
        if command == 'mode_play':
            if not (unmute_response.ok and play_response.ok):
                logger.error(f"Failed to execute 'mode_play' command. Unmute/playback mode response: {unmute_response.status_code}, Play response: {play_response.status_code}")
            else:
                logger.info(f"'mode_play' command executed successfully.")
        else:
            if not response.ok:
                logger.error(f"Failed to execute player command '{command}'. Response status: {response.status_code}")
            else:
                logger.info(f"Player command '{command}' executed successfully.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending command to player: {e}")

def insert_2s():
    logger.debug("Inserting 2s pause...")
    set_player('pause')
    time.sleep(2.1)
    set_player('play')
