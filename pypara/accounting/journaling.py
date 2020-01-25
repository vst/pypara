"""
This module provides data definitions and functionality related to journal entries and postings.
"""

__all__ = [
    "Direction",
    "JournalEntry",
    "Posting",
]

from dataclasses import dataclass, field
from enum import Enum
from typing import List, TypeVar, Generic, Iterable, Set, Dict

from .accounts import Account, AccountType
from ..commons.numbers import Amount, Quantity, isum
from ..commons.others import Guid, makeguid
from ..commons.zeitgeist import Date

#: Defines a type variable.
_T = TypeVar("_T")


class Direction(Enum):
    """
    Provides an enumeration for indicating increment and decrement events.
    """

    #: Declares the value type.
    value: int

    #: Indicates increment events.
    INC = 1

    #: Indicates decrement events.
    DEC = -1

    @classmethod
    def of(cls, quantity: Quantity) -> "Direction":
        """
        Returns the corresponding direction as per the sign of the quantity.

        :param quantity: Quantity to find the direction of.
        :return: Direction for the quantity.
        :raises AssertionError: If quantity is zero.
        """
        assert not quantity.is_zero()
        return Direction.INC if quantity > 0 else Direction.DEC


#: Provides the mapping for DEBIT/CREDIT convention as per increment/decrement and account type.
_debit_mapping: Dict[Direction, Set[AccountType]] = {
    Direction.INC: {AccountType.ASSETS, AccountType.EQUITIES, AccountType.LIABILITIES},
    Direction.DEC: {AccountType.REVENUES, AccountType.EXPENSES},
}


@dataclass(frozen=True)
class Posting(Generic[_T]):
    """
    Provides a posting value object model.
    """

    #: Journal entry the posting belongs to.
    journal: "JournalEntry[_T]"

    #: Account of the posting.
    account: Account

    #: Direction of the posting.
    direction: Direction

    #: Posted amount (in absolute value).
    amount: Amount

    @property
    def is_debit(self) -> bool:
        """
        Indicates if this posting is a debit.
        """
        return self.account.type in _debit_mapping[self.direction]

    @property
    def is_credit(self) -> bool:
        """
        Indicates if this posting is a credit.
        """
        return not self.is_debit


@dataclass(frozen=True)
class JournalEntry(Generic[_T]):
    """
    Provides a journal entry model.
    """

    #: Date of the entry.
    date: Date

    #: Description of the entry.
    description: str

    #: Business object as the source of the journal entry.
    source: _T

    #: Postings of the journal entry.
    postings: List[Posting[_T]] = field(default_factory=list, init=False)

    #: Globally unique, ephemeral identifier.
    guid: Guid = field(default_factory=makeguid, init=False)

    @property
    def increments(self) -> Iterable[Posting[_T]]:
        """
        Incerement event postings of the journal entry.
        """
        return (p for p in self.postings if p.direction == Direction.INC)

    @property
    def decrements(self) -> Iterable[Posting[_T]]:
        """
        Decrement event postings of the journal entry.
        """
        return (p for p in self.postings if p.direction == Direction.DEC)

    def post(self, account: Account, quantity: Quantity) -> "JournalEntry[_T]":
        """
        Posts an increment/decrement event (depending on the sign of ``quantity``) to the given account.

        If the quantity is ``0``, nothing is posted.

        :param account: Account to post the amount to.
        :param quantity: Signed-value to post to the account.
        :return: This journal entry (to be chained conveniently).
        """
        if not quantity.is_zero():
            self.postings.append(Posting(self, account, Direction.of(quantity), Amount(abs(quantity))))
        return self

    def validate(self) -> None:
        """
        Performs validations on the instance.

        :raises AssertionError: If the journal entry is inconsistent.
        """
        assert isum(i.amount for i in self.increments) == isum(i.amount for i in self.decrements)
