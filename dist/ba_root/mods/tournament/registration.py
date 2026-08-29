from server.enums import TeamStatus
from server.storage import Storage
from tournament.storage import SEASONS_DIR


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
        # team_id = f"team-{len(db['teams']) + 1}"
        # we use team-name as team-id
        team_id = team_name

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
            "id": team_id,
            "captain": captain_discord_id,
            "status": TeamStatus.IN_INVITATION if size > 1 else TeamStatus.UNVERIFIED,
            "members": members,
        }
        self.commit(db)
        return team_id

    def delete(self, team_id: str) -> str:
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
        del db["teams"][team_id]
        self.commit(db)
        return captain

    def accept(self, discord_id: str, account_id: str) -> bool:
        """accepts invitation from a team."""
        if not self.verify_account(account_id=account_id):
            return
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

    def verify_account(self, account_id: str) -> bool:
        """verifies the account with ballistica api."""
        import requests

        url = f"https://account.thecardinal.workers.dev/{account_id}"
        response = requests.get(url=url)
        return response.status_code == 200
