"""Thin typed wrappers around PyJWT's module-level functions.

PyJWT exposes ``encode`` and ``decode`` via a module-level ``__getattr__``
proxy, which pyright (strict mode) cannot fully type.  Isolating the two calls
here keeps the ``# type: ignore`` comments in one place and lets all other code
remain fully typed.
"""

from __future__ import annotations

from typing import Any

import jwt


def jwt_encode(payload: dict[str, Any], secret: str, algorithm: str) -> str:
    result: str = jwt.encode(payload, secret, algorithm=algorithm)  # type: ignore[reportUnknownMemberType]
    return result


def jwt_decode(token: str, secret: str, algorithms: list[str]) -> dict[str, Any]:
    result: dict[str, Any] = jwt.decode(  # type: ignore[reportUnknownMemberType]
        token, secret, algorithms=algorithms
    )
    return result
