# Octo Valley Randomizer
<img src="assets/repo_assets/Octo Valley Randomizer logo.png?raw=true" width="70%">

A randomizer for Splatoon 1's Octo Valley singleplayer campaign with a basic GUI.
<img src="wiki_assets/img/using_rando_screenshot1.png?raw=true?raw=true" width="70%">

## Features
As of writing, these are the aspects that are able to be randomized/shuffled:
- Kettles (bosses as well, though the boss kettles are randomized with each other with the exception of DJ Octavio, who is still the final boss)
- Ink colors (with the option to choose the color sets from either Octo Valley or multiplayer battles)
- Mission dialogue
- Stage music
- Hero Weapons (the Hero Shot, Hero Roller, and Hero Charger)

## Prerequisites 

Requires at least [Python 3.12](https://www.python.org/downloads/release/python-3127/) with the following dependencies installed from pip: 

- PyQt5
- ruamel.yaml
- PylibMS 
- oead
- requests
- packaging

Upon running the randomizer, the program will check all of the above dependencies installed and if not, offer to install them should the user agree to do so.

Alternatively, you can also run `python3 -m pip install --r requirements.txt` (`python3` is to be replaced with `py -3` if you're on Windows) beforehand to install of the dependencies for you.

This randomizer is compatiable with both real Wii U hardware using Aroma custom firmware (installation guide can be found [here](https://wiiu.hacks.guide/)) and the Cemu emulator. If you need details on how to legally obtain the files required to use the randomizer, consult [this guide](https://github.com/techmuse8/Octo-Valley-Randomizer/wiki/Dumping-Files-for-the-Randomizer) on the wiki. 

The randomizer supports any region of the game on the latest update (version 2.12.1 as of writing). Any version other than 2.12.1 will not work with the randomizer, as the program will check on whether the required files are valid or not.

## Usage

Please consult [the wiki](https://github.com/techmuse8/Octo-Valley-Randomizer/wiki) for information on how to use the randomizer tool and applying the randomizer patch onto your copy of the game.

## Credits

- [Pirlo](https://twitter.com/0x1CAA9C5C) - Making a patch that lets the Hero Roller work properply in singleplayer
- [Archipelago Discord Server](https://discord.gg/8Z65BR2) - Feedback, feature suggestions
