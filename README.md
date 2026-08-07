# EntityX Bombsquad Server Scripts
- script version: 1.7.61
- protocol version: 36 (v1 accounts not allowed.)

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

### Assign permissions
```
chmod 777 dist/bombsquad_headless
chmod 777 bombsquad_server
```

### Run the server.
```
tmux
./bombsquad_server
```

