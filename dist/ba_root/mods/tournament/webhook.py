from server.storage import Storage
from server import config
from tournament.storage import SEASONS_DIR
import requests


class Webhook(Storage):
    """webhook class for sending/editing/deleting messages."""

    def __init__(self, season_id: str) -> None:
        super().__init__("webhooks.json", SEASONS_DIR / season_id)
        self.dashboard_url = config.discord.webhooks.dashboard
        self.results_url = config.discord.webhooks.results
        self.session = requests.Session()

    def send(self, type: str, key: str, payload: dict) -> None:
        """sends a message to the webhook."""
        if type == "results":
            url = self.results_url
        else:
            url = self.dashboard_url

        db = self.read()
        if key in db:
            return
        response = self.session.post(url=f"{url}?wait=true", json=payload)
        db[key] = {
            "message_id": response.json()["id"],
            "url": url,
        }
        self.commit(db)

    def edit(self, key: str, payload: dict) -> None:
        """edits a message from webhook."""
        data = self.get(key)
        if not data:
            return
        url = self.message_url(data["url"], data["message_id"])
        self.session.patch(url=url, json=payload)

    def delete(self, key: str) -> None:
        """deletes a message from webhook."""
        db = self.read()
        data = db.get(key)
        if not data:
            return
        url = self.message_url(data["url"], data["message_id"])
        self.session.delete(url=url)
        del db[key]
        self.commit(db)

    def message_url(self, url: str, message_id: str) -> str:
        """returns the message url for the webhook."""
        return f"{url}/messages/{message_id}"

    def get(self, key: str) -> dict | None:
        """returns the webhook data for the key."""
        db = self.read()
        return db.get(key)