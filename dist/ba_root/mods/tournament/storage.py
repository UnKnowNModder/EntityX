""" storages for handling tournament data. """

from server.storage import Storage
from tournament.schema import SeasonSchema, TournamentSchema
from server.enums import TournamentStage
from typing import override
from pathlib import Path
from secrets import randbelow

SEASONS_DIR = Path("tournament") / "Seasons"

class Tournament(Storage):
    """ reads/writes json files. """

    def __init__(self):
        super().__init__("tournament.json", SEASONS_DIR)

    
    def bootstrap(self):
        """ creates the file if not already existing. """
        if not self.path.exists():
            data = self.read()
            self.commit(data)

    @override
    def read(self, external_path = None) -> TournamentSchema:
        """ reads from the file and returns schema"""
        data = super().read(external_path=external_path)
        return TournamentSchema.from_dict(data=data)

    @override
    def commit(self, data: TournamentSchema, external_path = None) -> None:
        """ commits the schema to the file as dict."""
        super().commit(data=data.to_dict(), external_path=external_path)

    def create_season(self, schema: SeasonSchema) -> None:
        """ creates the season with the given schema"""
        data = self.read()
        # we get the next season count safely.
        season_id = str(max([int(id) for id in data.seasons.keys()], default=0) + 1)

        data.seasons[season_id] = schema
        # activate this season
        data.active_season = season_id

        self.commit(data)

        # create the directory of the season
        season_dir = self.directory / season_id
        season_dir.mkdir(parents=True, exist_ok=True)

    def get_season(self, season_id: str) -> SeasonSchema | None: 
        """ returns a seasonschmea by its id"""
        data = self.read()
        season = data.seasons.get(season_id)

        if season:
            return season

    def update_season(self, season_id: str, season: SeasonSchema) -> None:
        """ updates a season using the given seasonschema."""
        data = self.read()
        data.seasons[season_id] = season
        self.commit(data)

tournament = Tournament()

class Registration(Storage):
    """ storage class for registration"""
    def __init__(self, season_id: str):
        super().__init__("registrations.json", SEASONS_DIR / season_id)
        self.bootstrap()

    def bootstrap(self):
        """ creates the file if not already existing. """
        if not self.path.exists():
            data = {
                "pre-registered": {},
                "registered": {}
            }
            self.commit(data)

    def pre_register(self, account_id: str, discord_user_id: str) -> bool | None:
        """ pre registers a user for verification to be registered."""
        database = self.read()
        pre_registered = database["pre-registered"]
        if discord_user_id in database["registered"]:
            # incase the user is already registered
            return False
        elif not discord_user_id in pre_registered:
            # pre-register
            pre_registered[discord_user_id] = account_id
            self.commit(data=database)
            return True

    def verify(self, account_id: str, device_uuid: str) -> bool:
        """ verifies and registers"""
        database = self.read()
        pre_registered = database["pre-registered"]
        for key, value in list(pre_registered.items()):
            if value == account_id:
                database["registered"][key] = {
                    "account_id": account_id,
                    "device_uuid": device_uuid
                }
                del pre_registered[key]
                self.commit(data=database)
                return True

        # seems like we did not match any account-id
        return False

