# EntityX Bombsquad Server Scripts
- script version: 1.7.61
- protocol version: 36 (game versions below script version won't be allowed to join)

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

[![Discord](https://img.shields.io/badge/Discord-Join%20Chat-7289DA?style=for-the-badge&logo=discord&logoColor=white&labelColor=7289DA)](https://discord.gg/yrYqbSU7wT)

# Installation:
### Quick one-line installation
```
curl -fsSL https://install.thecardinal.workers.dev | bash
```

- you may now change mods_config.json to your liking.

### Cd into the directory
```
cd EntityX
```

### Open a tmux session (you should always do this when starting the server)
```
tmux
```

### Run the server.
```
./bombsquad_server
```

# Discord bot:
- runs the bot on a second process. (the server won't lag)
- uses socket tunnel to pass the payload through.
- you can toggle the bot and configure the owner-id and bot token in mods_config.json

## bot commands
- /cmd <enter your chat-command to be send to game server.> (it runs according to the authority of the user.)
- /say <your chat message> (you can send a chat message to the game directly.)
- /owner or /admin <mention the user> (adds/removes from the owners or admins)
- /list (to receive list of players inside the game)