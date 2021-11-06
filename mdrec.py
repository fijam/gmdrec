#!/usr/bin/python3
import argparse
import functools
import signal
import sys
import time

from webapi import *
from settings import PRESS, OFFSET
from digipot import *

try:
    ad5245 = hardware_setup()
except NameError:
    print("Initialization skipped")
else:
    shutdown_pot(ad5245)

try:
    from gooey import Gooey
    have_gooey = True
except ImportError:
    have_gooey = False

# pyinstaller binaries need flushing
print = functools.partial(print, flush=True)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('label', default='%artist% - %title%',
                        help='Track format (e.g. %track number% - %title%)')
    parser.add_argument('recorder', default='R70/90/91', choices=['R70/90/91', 'R70/90/91 JPN', 'R700/701/900'],
                        help='Sony portable model')
    parser.add_argument('--disc-title', dest='disc_title', action='store',
                        help='Album title')
    parser.add_argument('--language-hint', dest='lang_code',
                        help='Transliteration hint (e.g. JA)')
    parser.add_argument('--only_label', default='OFF', dest='label_mode', choices=['OFF', 'ON', 'ERASE'],
                        help='Label a recorded disc')
    parser.add_argument('--no-tmarks', dest='no_tmarks', action='store_true',
                        help='Add 2s of silence instead of TMarks between tracks')
    return parser.parse_args()


def main():
    args = parse_arguments()
    import settings
    settings.recorder = args.recorder
    from hardware import push_button, enter_labelling, input_string, cleanup_exit, enter_rec_stby

    try:
        check_connection()
        print('Wait for REC Standby...')
        if have_gooey:
            print('Progress: -1/1')
        if args.label_mode == 'OFF':
            enter_rec_stby()
            time.sleep(8)
        print('The following tracks will be labelled:')
        (playlist_ID, track_no) = request_playlist_info()
        (tracklist, tracklist_time) = request_playlist_content(playlist_ID, track_no, args)

        push_button('Pause', PRESS, 1)  # start recording
        if args.label_mode == 'OFF':
            set_mode_play(playlist_ID)  # start playlist on first item

        for track_number, track in enumerate(tracklist):
            try:
                print(f'Recording: {tracklist[track_number]}')
                print(f'Progress: {track_number+1}/{len(tracklist)}')

                if args.label_mode in ['ON', 'ERASE']:
                    push_button('Play', PRESS, 1)
                    time.sleep(0.1)
                    push_button('Pause', PRESS, 1)
                    time.sleep(0.1)
                    enter_labelling()
                    if args.label_mode == 'ERASE':
                        push_button('Playmode', PRESS, 128)
                    input_string(tracklist[track_number])
                    if track_number + 1 != len(tracklist):
                        push_button('Right', PRESS, 1)
                    else:
                        push_button('Stop', PRESS, 1)

                if args.label_mode == 'OFF':
                    enter_labelling()
                    input_string(tracklist[track_number])
                    track_remaining = request_track_time()
                    print(f'Track labelled. Time to TMark: {track_remaining:0.0f}s')
                    time.sleep(track_remaining - OFFSET)  # adjust OFFSET if TMark is too early or too late
                    if track_number+1 != len(tracklist):
                        if args.no_tmarks:
                            set_player('pause')
                            time.sleep(2.1)
                            set_player('play')
                        push_button('TMark', PRESS, 1)
                    else:  # last track, save TOC
                        push_button('Stop', PRESS, 1)

            except KeyboardInterrupt:
                # Catch interrupt generated by Gooey on pressing the Stop button
                push_button('Stop', PRESS, 1)
                set_player('stop')
                print('Cleaning up.')
                sys.exit()

        print('Waiting for TOC to save...')
        if have_gooey:
            print('Progress: -1/1')
        time.sleep(12)
        if args.disc_title is not None:
            print('Labelling album title...')
            enter_labelling()
            if args.label_mode == 'ERASE':
                push_button('Playmode', PRESS, 128)
            input_string(args.disc_title)
            push_button('Stop', PRESS, 1)
            time.sleep(8)

    finally:
        # shut down the digital pot and quit
        cleanup_exit()


if __name__ == '__main__':
    if have_gooey:
        main = Gooey(program_description='Record and label MDs on Sony portable recorders',
                     tabbed_groups=False,
                     progress_regex=r"^Progress: (?P<current>-?\d+)/(?P<total>\d+)$",
                     progress_expr="current / total * 100",
                     hide_progress_msg=True,
                     optional_cols=2,
                     default_size=(460, 580),
                     show_success_modal=False,
                     shutdown_signal=signal.CTRL_C_EVENT)(main)
    main()
