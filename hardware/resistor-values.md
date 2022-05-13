Resistor Values
===============

The portable MD recorders detect the buttons based on the resistance between pin 2 and 4.


RM-MC11EL
---------

Source: Own measurements, 2022-05-13

No dedicated "play" button.

| Button     |  Ohms  |
| ---------- | ------ |
| prev/rew   |   1002 |
| sound      |   2302 |
| play/ffwd  |   3649 |
| pause      |   5163 |
| stop       |   7090 |
| vol-       |   8390 |
| vol+       |   9890 |
| display    |  16690 |
| playmode   |  14290 |
| rpt/ent    |  11890 |


gmdrec resistor values
----------------------

Source: Maz (Discord)

| Button     | Ohms  |
| ---------- | ----- |
| Play       |  ~200 |
| Prev/Back  |  1000 |
| Sound      |  2300 |
| Next/Fwd   |  3650 |
| Pause      |  5160 |
| Stop       |  7100 |
| Vol-       |  8400 |
| Vol+       |  9900 |
| TMark      | 11900 |
| Playmode   | 14300 |
| Display    | 16700 |
| Record     | 19500 |


RM-MZR30MP
----------

Source: [Sony MiniDisc® RM-MZR30MP Remote Control Hacked](http://www.minidisc.org/keep/)

| Function      | Ohms  |
| ------------- | ----- |
| Prev/Back     |  1000 |
| Next/Forward  |  3627 |
| Pause         |  5156 |
| Stop          |  7050 |
| Volume -      |  8400 |
| Volume +      |  9900 |
| Track Mark    | 11900 |

Not present on RM-MZR30MP, but understood by MZ-R30:

| Function      | Ohms  |
| ------------- | ----- |
| Mode          | 14000 |
| Display       | 17000 |
| Record        | 19500 |
| Test Mode     | 24000 |



MZ-N510 Behavior
----------------

This recorder's behavior differs with the same resistance values
when using RM-MC11EL compared to gmdrec + 100kOhm pulldown on
the LCD data line.

Note: The RM-MC11EL doesn't have a dedicated 200 Ohm "play" button,
the 3650 Ohm Play/FFwd "button" (jog "up" movement) is used as both
playback and next track toggle.


| Ohms  | RM-MC11EL  | gmdrec + 100kOhm pulldown on LCD data |
| ----- | ---------- | ------------------------------------- |
|  200  | -          | play/pause toggle                     |
| 3650  | starts playback if stopped/paused, goes to next track otherwise | goes to next track, even in paused/stopped state |
| 5160  | toggles pause only, does not start playback if stopped | works as GROUP button(?) |
