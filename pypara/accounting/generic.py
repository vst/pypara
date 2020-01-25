"""
This module provides definitions and functionality applicable to the broader accounting scope.
"""

__all__ = ["Balance"]

from dataclasses import dataclass

from pypara.commons.numbers import Quantity
from pypara.commons.zeitgeist import Date


@dataclass(frozen=True)
class Balance:
    """
    Provides a value object model for encoding dated balances.
    """

    #: Date of the balance.
    date: Date

    #: Value of the balance.
    value: Quantity
