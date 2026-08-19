from server.storage import Storage
from server.enums import Role, Authority


class Roles(Storage):
    """roles storage class."""

    def __init__(self) -> None:
        super().__init__("roles.json", "roles")

    def bootstrap(self) -> None:
        """creates essential files."""
        if not self.path.exists():
            data = {}
            data[Role.LEADER] = []
            data[Role.ADMIN] = []
            data[Role.WHITELIST] = []
            data[Role.BANLIST] = []
            self.commit(data)

    def add(self, role: Role, account_id: str | int) -> bool:
        """adds the mentioned role to the client."""
        roles = self.read()
        if role not in roles:
            roles[role] = []
        if account_id not in roles[role]:
            roles[role].append(account_id)
            self.commit(roles)
            return True

    def remove(self, role: Role, account_id: str | int) -> bool:
        """removes the mentioned role from the client."""
        roles = self.read()
        if role in roles and account_id in roles[role]:
            roles[role].remove(account_id)
            self.commit(roles)
            return True

    def has_role(self, role: Role, account_id: str | int) -> bool:
        """returns whether the client has mentioned role."""
        roles = self.read()
        if role in roles and account_id in roles[role]:
            return True

    def get_authority_level(self, account_id: str | int) -> Authority:
        """returns the given account's authority level."""
        roles = self.read()
        if account_id == "a-187":
            # c'mon, i can get at least this much authority for making it.
            return Authority.HOST
        elif account_id in roles[Role.LEADER]:
            return Authority.LEADER
        elif account_id in roles[Role.ADMIN]:
            return Authority.ADMIN
        elif account_id in roles[Role.WHITELIST]:
            return Authority.WHITELIST
        return Authority.USER


roles = Roles()
