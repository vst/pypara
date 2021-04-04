"""
This module defines type definitions and functions for various purposes.
"""

__all__ = ["Guid", "identity", "makeguid"]

from typing import NewType, TypeVar
from uuid import uuid4

#: Defines a new-type for globally-unique identifiers.
Guid = NewType("Guid", str)


def makeguid() -> Guid:
    """
    Creates a new :py:class:`Guid`.

    :return: :py:class:`Guid` instance.
    """
    return Guid(uuid4().hex)


#: Defines a type variable.
_T = TypeVar("_T")


def identity(x: _T) -> _T:
    """
    Provides the identity function.

    :param x: Any value of the generic type.
    :return: The value consumed.
    """
    return x
