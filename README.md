## Overview
gmdrec records and labels tracks on selected Sony portable MD recorders.

Compatible models include: R70, R90, R91, R700, R701, R900

Support needs to be added: R910, R909, G755, G750, R55, R37

## Demo

## How it works

You need:

- [Foobar2000](https://www.foobar2000.org/) (Windows) or [DeaDBeeF](https://deadbeef.sourceforge.io/) (Linux/macOS) music player
- [beefweb](https://github.com/hyperblast/beefweb) plugin for the music player
- an interface circuit that emulates the remote (see below)
- gmdrec

gmdrec uses an API provided by the beefweb plugin to remotely control a music player. It grabs the track names from a playlist and breaks them down into a sequence of buttons to press. These are translated by the interface circuit into signals recognized by the MD recorder.

### Interface circuit

The circuit comprises a USB-I2C bridge and a I2C digital potentiometer as well as a few passive components.
 
The schematics and PCB files are provided in the hardware directory.

You can build it yourself or get a preassembled one from me directly.

### Software

**label**: You can specify how the tracks should be formatted. The default is `%artist% - %title%` but you can use any combination of fields from [here](https://wiki.hydrogenaud.io/index.php?title=Foobar2000:Title_Formatting_Reference#Remapped_metadata_fields).

**disc_title**: Optionally, the album title can be provided. The disc title will be saved after labelling of the tracks is finished.

**lang_code**: By default, gmdrec will attempt to transliterate non-latin scripts. As some languages use the same characters (e.g. Japanese and Chinese) you can specify a [two letter language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) to make it more accurate.

**no_tmarks**: By default, gmdrec will insert a Track Mark at the end of every track. If there is a period of silence between the tracks the recorder itself will enter another, resulting in duplicates. 

**label_mode**: Optionally, you can use gmdrec to label a disc which has been already recorded. Make sure the number of items on the playlist equals the number of tracks on the MD. Set the recorder to the first track to be labelled.

### Recording a MiniDisc

1. Create a playlist you want to record.
2. Connect your PC audio output (toslink or analog) to the input on the MD recorder.
3. Connect the interface circuit to USB and to the remote connector on the MD recorder.
4. Launch gmdrec.

## Limitations

Limitations inherent to the MD format:

- up to 254 tracks per disk
- up to ~200 characters per track
- up to ~1700 total characters per disc
- limited character set (ASCII charaters excluding `[ \ ] ^ { | } ~`)

gmdrec will fail if track duration is too short to finish labelling in time. It takes about 30-40s to label a track. If you have a disc with many short tracks, consider first recording it and then using **label_mode** which pauses each track for labelling.

## Contributions welcome

Merge requests providing new functionality or support for additional devices are welcome. 

[!["Buy Me A Coffee"](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/fijam)

### Note: if you are looking for the older version of this project which relied on a Raspberry Pi, check out https://github.com/fijam/md-rec/
