## Overview
gmdrec records and labels tracks on selected Sony portable MD recorders.

Compatible models include: R55, R37, R70, R90, R91, R700, R701, R900, N707, R909, R910, N1, N707

**Note:** R909, R910 and N1 **require** [100k Ohm pulldown on the LCD data line.](https://github.com/fijam/gmdrec/wiki/Remote-connectors) 

With the new revision of the titler you just need to solder the jumper next to the 100k Ohm resistor.

Need to be tested: G755, G750

## Demo
[![title-card](https://user-images.githubusercontent.com/75824/136713970-b0210516-68b6-4405-a2c9-558976e5be58.png)](https://www.youtube.com/watch?v=6wfP5BtrBSM)

## How it works

You need:

- [Foobar2000](https://www.foobar2000.org/) (Windows) or [DeaDBeeF](https://deadbeef.sourceforge.io/) (Linux/macOS) music player
- [beefweb](https://github.com/hyperblast/beefweb) plugin for the music player
- an interface circuit that emulates the remote (see below)

gmdrec uses an API provided by the beefweb plugin to remotely control a music player. It grabs the track names from a playlist and breaks them down into a sequence of buttons to press. These are translated by the interface circuit into signals recognized by the MD recorder.

### Interface circuit

The circuit comprises a USB-I2C bridge and a I2C digital potentiometer as well as a few passive components. 

The schematics and PCB files are provided in the hardware directory. You can get a preassembled one from me directly.

### Software
![gmdrec-v0 3](https://user-images.githubusercontent.com/75824/140431457-25fa2b6e-e49f-4961-b3a1-644eece69dab.png)


**label**: Specify how the tracks should be formatted. You can use any combination of fields from [here](https://wiki.hydrogenaud.io/index.php?title=Foobar2000:Title_Formatting_Reference#Remapped_metadata_fields).

**recorder**: Select your recorder model. Note that some devices may [behave differently depending on firmware](https://github.com/fijam/gmdrec/wiki/Troubleshooting#firmware-revisions).

**disc_title**: Optionally, the disc can be labelled with an album title.

**lang_code**: By default, gmdrec will attempt to transliterate non-latin scripts. As some languages share the same characters (e.g. Japanese and Chinese) you can specify a [two-letter language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) to make it more accurate.

**label_mode**: Optionally, you can use gmdrec to label a disc which has been already recorded. Make sure the number of items on the playlist equals the number of tracks on the MD and set the recorder to the first track to be labelled. If you select `ERASE`, old track names will be deleted before labelling.

**no_tmarks**: By default, gmdrec will insert a Track Mark at the end of every track. If there is a period of silence between the tracks the recorder itself will enter another, resulting in duplicates. This option adds 2 seconds of silence between each track and making track marks is left to the recorder. *Strongly recommended for R909/R910/N1.*

**--ignore-gooey**: Optionally, you can run the software directly in console without the GUI.

### Recording a MiniDisc

1. Create a playlist you want to record.
2. Connect your PC audio output (toslink or analog) to the input on the MD recorder.
3. Connect the interface circuit to USB and to the remote connector on the MD recorder.
4. Start gmdrec.

## Linux

gmdrec works on GNU/Linux but requires some additional setup. Instructions are [on a separate wiki page.](https://github.com/fijam/gmdrec/wiki/Linux-setup)

## Limitations

Limitations of the MD format:

- up to 254 tracks per disk
- up to ~200 characters per track
- up to ~1700 total characters per disc
- limited character set: ASCII charaters excluding `[ \ ] ^ { | } ~`

gmdrec will fail if track duration is too short to finish labelling in time. It takes about 35 seconds to label a track. If you have a disc with many short tracks, consider recording it first and then using **label_mode** which pauses each track for labelling.

## Contributions welcome

Merge requests providing new functionality or support for additional devices are welcome. 


[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/fijam)

### Note: if you are looking for the older version of this project which relied on a Raspberry Pi, check out https://github.com/fijam/md-rec/
