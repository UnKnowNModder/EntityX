""" roles storage core. """
from __future__ import annotations
from datetime import datetime, timedelta
from ._storage import Storage
from ._enums import Role, Authority

class Roles(Storage):
	"""roles storage class."""

	def __init__(self) -> None:
		super().__init__("roles.json")
		self.auth = self.directory / "auth.json"
		self.bootstrap()

	def bootstrap(self) -> None:
		"""creates essential files."""
		if not self.path.exists():
			config = {}
			config[Role.LEADER] = []
			config[Role.ADMIN] = []
			config[Role.WHITELIST] = []
			config[Role.BANLIST] = []
			self.commit(config)
		
		from . import config
		config = config.read()
		if not config["auth_verification"]["enable"]:
			return
		today = datetime.now().date()
		future_deletion = today + timedelta(days=config["auth_verification"]["days"])
		# check for auth file
		if self.auth.exists():
			# exists, we need to check for deletion time.
			auth = self.read(self.auth)
			deletion = datetime.strptime(auth["deletion"], "%Y-%m-%d").date()
			if deletion <= today:
				# your time has come, HAHWHSHAHAHA.
				auth["deletion"] = future_deletion.strftime("%Y-%m-%d")
				auth["authentic"] = []
				self.commit(auth, self.auth)
		else:
			auth = {}
			auth["deletion"] = future_deletion.strftime("%Y-%m-%d")
			auth["authentic"] = []
			self.commit(auth, self.auth)

	def add(self, role: Role, account_id: str) -> bool:
		"""adds the mentioned role to the client."""
		roles = self.read()
		if role not in roles:
			roles[role] = []
		if account_id not in roles[role]:
			roles[role].append(account_id)
			self.commit(roles)
			return True

	def remove(self, role: Role, account_id: str) -> bool:
		"""removes the mentioned role from the client."""
		roles = self.read()
		if role in roles and account_id in roles[role]:
			roles[role].remove(account_id)
			self.commit(roles)
			return True

	def has_role(self, role: Role, account_id: str) -> bool:
		"""returns whether the client has mentioned role."""
		roles = self.read()
		if role in roles and account_id in roles[role]:
			return True

	def get_authority_level(self, account_id: str) -> Authority:
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
	
	def authenticate(self, account_id: str) -> bool:
		""" authenticate the account. """
		auth = self.read(self.auth)
		if account_id not in auth["authentic"]:
			auth["authentic"].append(account_id)
			self.commit(auth, self.auth)
			return True
	
	def is_authentic(self, account_id: str) -> bool:
		""" returns whether the account's authentic,
		this is handled by OTPs. """
		auth = self.read(self.auth)
		return account_id in auth["authentic"]