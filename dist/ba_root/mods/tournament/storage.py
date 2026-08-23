"""storages for handling tournament data."""

from pathlib import Path
from typing import override

from server.enums import TeamStatus
from server.storage import Storage
from tournament.schema import SeasonSchema, TournamentSchema

SEASONS_DIR = Path("tournament") / "seasons"


class Tournament(Storage):
    """reads/writes json files."""

    def __init__(self):
        super().__init__("tournament.json", SEASONS_DIR)

    def bootstrap(self):
        """creates the file if not already existing."""
        if not self.path.exists():
            self.commit(TournamentSchema())

    @override
    def read(self, external_path=None) -> TournamentSchema:
        """reads from the file and returns schema"""
        data = super().read(external_path=external_path)
        return TournamentSchema.from_dict(data=data)

    @override
    def commit(self, data: TournamentSchema, external_path=None) -> None:
        """commits the schema to the file as dict."""
        super().commit(data=data.to_dict(), external_path=external_path)

    def create_season(self, schema: SeasonSchema) -> None:
        """creates the season with the given schema"""
        data = self.read()
        # we get the next season count safely.
        season_id = str(max([int(id) for id in data.seasons], default=0) + 1)

        data.seasons[season_id] = schema
        # activate this season
        data.active_season = season_id

        self.commit(data)

        # create the directory of the season
        season_dir = self.directory / season_id
        season_dir.mkdir(parents=True, exist_ok=True)

    def get_season(self, season_id: str) -> SeasonSchema | None:
        """returns a seasonschmea by its id"""
        data = self.read()
        season = data.seasons.get(season_id)

        if season:
            return season

    def update_season(self, season_id: str, season: SeasonSchema) -> None:
        """updates a season using the given seasonschema."""
        data = self.read()
        data.seasons[season_id] = season
        self.commit(data)

    @property
    def are_registrations_open(self):
        """ as the name says"""
        return self.read().registrations_status

    def open_registrations(self):
        """ opens the registrations. """
        db = self.read()
        db.registrations_status = True
        self.commit(db)

    def close_registrations(self):
        """ closes the registrations. """
        db = self.read()
        db.registrations_status = False
        self.commit(db)

tournament = Tournament()

class Registration(Storage):
    """storage class for registration"""

    def __init__(self, season_id: str):
        super().__init__("registrations.json", SEASONS_DIR / season_id)
        self.bootstrap()

    def bootstrap(self):
        """creates the file if not already existing."""
        if not self.path.exists():
            data = {"teams": {}, "players": {}}
            self.commit(data)

    def is_registered(self, id: str) -> bool:
        """returns whether the discord user is already registered?"""
        db = self.read()
        players = db.get("players", {})
        return id in players

    def register(
        self,
        team_name: str,
        captain_discord_id: str,
        captain_account_id: str,
        invited_members: list = [],
    ):
        """registers a team/solo in database."""
        size = len(invited_members) + 1
        if self.is_registered(captain_discord_id) or any(
            self.is_registered(discord_id) for discord_id in invited_members
        ):
            # if any of them is registered, decline it.
            return

        db = self.read()
        team_id = f"team-{len(db['teams']) + 1}"

        captain = {
            "account_id": captain_account_id,
            "device_uuid": "",
            "discord_id": captain_discord_id,
        }
        db["players"][captain_discord_id] = team_id
        db["players"][captain_account_id] = team_id

        members = [captain]
        for discord_id in invited_members:
            members.append(
                {
                    "account_id": "",
                    "device_uuid": "",
                    "discord_id": discord_id,
                }
            )
            db["players"][discord_id] = team_id

        # saving in players dict will help us do team lookup and verification much faster.
        db["teams"][team_id] = {
            "name": team_name,
            "captain": captain_discord_id,
            "status": TeamStatus.IN_INVITATION if size > 1 else TeamStatus.UNVERIFIED,
            "members": members,
        }
        self.commit(db)
        return team_id

    def delete(self, team_id: str) -> tuple[str, str]:
        """deletes the team when someone declines the invitation."""
        db = self.read()
        team = db["teams"].get(team_id)

        for member in team["members"]:
            account_id = member["account_id"]
            if account_id in db["players"]:
                del db["players"][account_id]
            discord_id = member["discord_id"]
            if discord_id in db["players"]:
                del db["players"][discord_id]

        captain = team["captain"]
        name = team["name"]
        del db["teams"][team_id]
        self.commit(db)
        return captain, name

    def accept(self, discord_id: str, account_id: str) -> bool:
        """accepts invitation from a team."""
        db = self.read()
        # lookup team id from players map
        team_id = db["players"].get(discord_id)
        if not team_id:
            return False

        team = db["teams"].get(team_id)

        for member in team["members"]:
            if member["discord_id"] == discord_id:
                member["account_id"] = account_id

                # update in players map
                db["players"][account_id] = team_id

                # check if everyone on the team has joined.
                if all(m["account_id"] for m in team["members"]):
                    # update the team status
                    team["status"] = TeamStatus.UNVERIFIED

                self.commit(db)
                return True
        return False

    def verify(self, account_id: str, device_uuid: str) -> bool | None:
        """verifies the player"""
        db = self.read()
        team_id = db["players"].get(account_id)
        if not team_id:
            return False

        team = db["teams"].get(team_id)

        for member in team["members"]:
            if member["account_id"] == account_id:
                # case: the guy is already verified
                if member["device_uuid"]:
                    return None
                member["device_uuid"] = device_uuid

                # check if everyone on the team has verified.
                if all(m["device_uuid"] for m in team["members"]):
                    # update the team status
                    team["status"] = TeamStatus.VERIFIED

                self.commit(db)
                return True
        return False
