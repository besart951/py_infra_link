from __future__ import annotations

import bcrypt


class BcryptPasswordHasher:
    """Production password hasher using bcrypt."""

    def hash(self, raw_password: str) -> str:
        return bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

    def verify(self, raw_password: str, hashed: str) -> bool:
        return bcrypt.checkpw(raw_password.encode(), hashed.encode())


class PlainPasswordHasher:
    """Test-only password hasher — stores a prefixed plain text string.

    Never use this in production.  The prefix ensures tests cannot accidentally
    accept real bcrypt hashes as valid credentials.
    """

    _PREFIX = "plain:"

    def hash(self, raw_password: str) -> str:
        return f"{self._PREFIX}{raw_password}"

    def verify(self, raw_password: str, hashed: str) -> bool:
        return hashed == f"{self._PREFIX}{raw_password}"
