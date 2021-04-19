__all__ = ["identity"]

from typing import TypeVar

#: A named, generic type variable.
_T = TypeVar("_T")


def identity(x: _T) -> _T:
    """
    Provides the identity function.

    :param x: Any value of the generic type.
    :return: The value consumed.

    >>> identity(1)
    1
    """
    return x
