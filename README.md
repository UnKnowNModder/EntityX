# EntityX Bombsquad Server Scripts
- script version: 1.7.61
- protocol version: 36 (game versions below script version won't be allowed to join)

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

[![Discord](https://img.shields.io/badge/Discord-Join%20Chat-7289DA?style=for-the-badge&logo=discord&logoColor=white&labelColor=7289DA)](https://discord.gg/yrYqbSU7wT)

# Installation:
### Install dependencies
```
sudo apt-get update
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.13 python3.13-dev python3.13-venv
```
### Clone the repository
```
git clone https://github.com/UnKnowNModder/EntityX.git
```

- you may now change config.toml to your needs.

### cd into the directory
```
cd EntityX
```

### open a tmux session
```
tmux
```

### Run the server.
- note: the config.json will be created after the first run. so run it first time and kill the process using ```mgr.shutdown()``` and configure your settings there and run again.
```
./bombsquad_server
```

# Discord bot:
- it requires uv (the script will download automatically if you don't have it installed)
- runs the bot on a second process. (the server won't lag)
- uses socket tunnel to pass the payload through.
- you can toggle the bot and configure the owner-id and bot token in config.json found in dist/ba_root/mods/

## bot commands
- /cmd <enter your chat-command to be send to game server.> (it runs according to the authority of the user.)
- /say <your chat message> (you can send a chat message to the game directly.)
- /owner or /admin <mention the user> (adds/removes from the owners or admins)
- /list (to receive list of players inside the game)