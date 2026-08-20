from datetime import datetime, timedelta

from server import config
from server.storage import Storage


class Auth(Storage):
    """auth storage class."""

    def __init__(self):
        super().__init__("auth.json", "roles")

    def bootstrap(self):
        """initializes auth file or resets based on expiry"""
        if not config.otp_verification.enable:
            return

        today = datetime.now().date()
        future_deletion = today + timedelta(days=config.otp_verification.days)
        # check if file exists
        if not self.path.exists():
            # we need to make one.
            data = {"deletion": future_deletion.strftime("%Y-%m-%d"), "authentic": []}
            self.commit(data)
            return

        # exists, we need to check for deletion time.
        data = self.read()
        deletion = datetime.strptime(data["deletion"], "%Y-%m-%d").date()
        if today >= deletion:
            # your time has come, HAHWHSHAHAHA.
            data["authentic"] = []
            data["deletion"] = future_deletion.strftime("%Y-%m-%d")
            self.commit(data)

    def authenticate(self, account_id: str) -> bool:
        """authenticate the account."""
        auth = self.read()
        if account_id not in auth["authentic"]:
            auth["authentic"].append(account_id)
            self.commit(auth)
            return True

    def is_authentic(self, account_id: str) -> bool:
        """returns whether the account's authentic,
        this is handled by OTPs."""
        auth = self.read()
        return account_id in auth["authentic"]


auth = Auth()
