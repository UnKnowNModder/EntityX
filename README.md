# Bombsquad Server Scripts
it's a modified version server scripts
it has a few features and utilities described below.
- script version: 1.7.48

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
[![Discord](https://img.shields.io/badge/Discord-Join%20Chat-7289DA?style=for-the-badge&logo=discord&logoColor=white&labelColor=7289DA)](https://discord.gg/yrYqbSU7wT)

## ⚙️ Installation
```git clone https://github.com/UnKnowNModder/EntityXScript.git && cd EntityXScript && git checkout dev && python3 -m pip install -U discord.py --target /home/sanju/EntityXScript/dist/ba_data/python-site-packages && chmod +x ballisticakit_server dist/ballisticakit_headless
```

## Features:
- has important commands
- tournament system
- protection (v2 check)
- session leave/join messages has been removed (note: party messages would still be visible)
- once a week OTP verification for every player.

## Tournament System:
- it's a tournament system, that uses a different session for matches.
- the support for adding matches through discord bot will be added soon
### Features:
- the participants can simply do /confirm in-game to confirm their presence in the tournament match.
- once all the participants of a match have been confirmed, the match will begin.
- if any player lefts in between the tournament match, he'll be given 15 minutes to join back, exceeded the time, the team will be disqualified.
- once match starts, it can only be stopped by restarting the server (will add other way in upcoming commits).

# Todo:
- add support for discord bot
- refine the tournament system to allow participants to agree on player leaves if they want, overriding the default leave-win system.


## Modification?
- yup, you can modify it and use however you want in your scripts.
- whether you need to take a bit of idea to copy paste some code, you can do it all.
- (credit isn't needed just so you know)