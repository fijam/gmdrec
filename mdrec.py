#!/usr/bin/python3
"""This is the main module of gmdrec."""

__version__ = '0.7.2'

import argparse
import functools
import logging
import signal
import sys
import time
from pprint import pprint

from hardware import pulldown_on_data, cleanup_exit

try:
    from gooey import Gooey
    have_gooey = True
except ImportError:
    have_gooey = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# pyinstaller binaries need flushing
print = functools.partial(print, flush=True)

# pyinstaller needs to be told to use utf-8
sys.stdout.reconfigure(encoding='utf-8')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('label', default='%artist% - %title%',
                        help='Format of track labels')
    parser.add_argument('recorder', default='R70 through N707', choices=['R55/R37',
                                                                         'R55/R37 JPN',
                                                                         'R70 through N707',
                                                                         'R70 through N707 JPN',
                                                                         'R909/R910/N1',
                                                                         'R909/R910/N1 JPN'],
                        help='Sony MD recorder model')
    parser.add_argument('--disc-title', dest='disc_title', action='store',
                        help='for labelling a disc')
    parser.add_argument('--language-hint', dest='language_code',
                        help='for transliteration')
    parser.add_argument('--only_label', default='OFF', dest='label_mode', choices=['OFF', 'ON', 'ERASE'],
                        help='for disc relabelling')
    parser.add_argument('--no-tmarks', dest='no_tmarks', action='store_true',
                        help='Add 2s of silence instead of TMarks between tracks')
    return parser.parse_args()

def setup_logging(args):
    if args.debug:
        logger.setLevel(logging.DEBUG)
    logger.debug("Debugging enabled.")



def main():
    args = parse_arguments()
    setup_logging(args)

    import settings
    settings.recorder = args.recorder
    from logic import enter_labelling, sanitize_tracklist, sanitize_track, input_string, enter_rec_stby, pause_unpause, erase, write_toc, tmark_it, next_track
    from webapi import check_connection, request_playlist_content, request_track_time, set_player, insert_2s

    try:
        logger.info("Starting gmdrec...")
        if have_gooey: print('Progress: -1/1')
        check_connection()
        tracklist = request_playlist_content(args)
        tracklist = sanitize_tracklist(tracklist, args.language_code)
        #print('The playlist contains the following tracks:')
        logger.info('The playlist contains the following tracks:')
        pprint(tracklist)

        if args.recorder in ['R909/R910/N1', 'R909/R910/N1 JPN']:
            pulldown_on_data(True)

        if args.label_mode == 'OFF':
            print('Wait for REC Standby...')
            enter_rec_stby()
            pause_unpause()  # start recording
            set_player('mode_play')  # start playlist on first item
            for track_number, track in enumerate(tracklist):
                print(f'Recording: {tracklist[track_number]}')
                print(f'Progress: {track_number+1}/{len(tracklist)}')
                enter_labelling()
                input_string(tracklist[track_number])
                track_remaining = request_track_time()
                print(f'Track labelled. Time to TMark: {track_remaining:0.0f}s')
                time.sleep(track_remaining)
                if track_number + 1 != len(tracklist):
                    insert_2s() if args.no_tmarks else tmark_it()
                else:
                    write_toc()

        if args.label_mode in ['ON', 'ERASE']:
            print('Pause on the first track you want to label. Labelling will begin in 5s')
            time.sleep(5)
            for track_number, track in enumerate(tracklist):
                print(f'Labelling: {tracklist[track_number]}')
                print(f'Progress: {track_number + 1}/{len(tracklist)}')
                pause_unpause()
                time.sleep(0.1)
                pause_unpause()
                enter_labelling()
                if args.label_mode == 'ERASE': erase()
                input_string(tracklist[track_number])
                if track_number + 1 != len(tracklist):
                    next_track()
                else:
                    write_toc()

        if have_gooey: print('Progress: -1/1')

        if args.disc_title is not None:
            disc_title = sanitize_track(args.disc_title, args.language_code)
            print(f'Labelling the disc: {disc_title}')
            enter_labelling()
            if args.label_mode == 'ERASE': erase()
            input_string(disc_title)
            write_toc()

    except KeyboardInterrupt:
        # Catch interrupt generated by Gooey on pressing the Stop button
        logger.warning("Keyboard interrupt received, stopping player and writing TOC.")
        set_player('stop')
        write_toc()

    finally:
        logger.info("Cleaning up and exiting.")
        # shut down the digital pot and quit
        cleanup_exit()


if __name__ == '__main__':
    if have_gooey:
        main = Gooey(program_description='Record and label MDs on Sony portable recorders',
                     menu=[{
                         'name': 'About',
                         'items': [{
                             'type': 'AboutDialog',
                             'menuTitle': 'Version',
                             'name': 'gmdrec',
                             'description': 'Record and label MDs on Sony portable recorders',
                             'version': __version__,
                             'copyright': '©2021 fijam',
                             'website': 'https://github.com/fijam/gmdrec',
                             'license': 'BSD-3-Clause'
                         }]
                     }],
                     tabbed_groups=False,
                     progress_regex=r"^Progress: (?P<current>-?\d+)/(?P<total>\d+)$",
                     progress_expr="current / total * 100",
                     hide_progress_msg=True,
                     optional_cols=3,
                     default_size=(460, 550),
                     show_success_modal=False,
                     shutdown_signal=signal.CTRL_C_EVENT)(main)
    main()
