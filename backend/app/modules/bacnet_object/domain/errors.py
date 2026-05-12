from __future__ import annotations

from app.shared.errors import DomainError


class BacnetObjectError(DomainError):
    """Base class for BACnet object domain errors."""


class BacnetObjectNotFoundError(BacnetObjectError):
    """Raised when a BACnet object is not found."""


class BacnetObjectInstanceConflictError(BacnetObjectError):
    """Raised when a (object_type, object_instance) pair already exists on the same device."""


class BacnetObjectNameConflictError(BacnetObjectError):
    """Raised when a BACnet object name already exists on the same field device."""


class InvalidBacnetObjectNameError(BacnetObjectError):
    """Raised when a BACnet object name is invalid."""


class InvalidBacnetObjectInstanceError(BacnetObjectError):
    """Raised when a BACnet object instance number is invalid."""


class FieldDeviceDoesNotExistError(BacnetObjectError):
    """Raised when the parent field device does not exist."""
