"""
This module provides data definitions and related functionality for preparing general ledgers.
"""

__all__ = [
    "GeneralLedger",
    "Ledger",
    "LedgerEntry",
    "build_general_ledger",
]

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, Generic, Iterable, List, Optional, TypeVar

from ..commons.numbers import Amount, Quantity
from ..commons.zeitgeist import Date
from .accounts import Account
from .generic import Balance
from .journaling import JournalEntry, Posting

#: Defines a type variable.
_T = TypeVar("_T")


@dataclass
class LedgerEntry(Generic[_T]):
    """
    Provides a ledger entry model.
    """

    #: Ledger the entry belongs to.
    ledger: "Ledger[_T]"

    #: Posting of the ledger entry.
    posting: Posting[_T]

    #: Balance of the ledger entry.
    balance: Quantity

    @property
    def date(self) -> Date:
        """
        Date of the ledger entry.
        """
        return self.posting.journal.date

    @property
    def description(self) -> str:
        """
        Description of the ledger entry.
        """
        return self.posting.journal.description

    @property
    def amount(self) -> Amount:
        """
        Amount of the ledger entry.
        """
        return self.posting.amount

    @property
    def cntraccts(self) -> List[Account]:
        """
        Counter accounts for the ledger entry.
        """
        return [p.account for p in self.posting.journal.postings if p.direction != self.posting.direction]

    @property
    def is_debit(self) -> bool:
        """
        Indicates if the ledger entry is a debit.
        """
        return self.posting.is_debit

    @property
    def is_credit(self) -> bool:
        """
        Indicates if the ledger entry is a credit.
        """
        return self.posting.is_credit

    @property
    def debit(self) -> Optional[Amount]:
        """
        Returns the debit amount, if any.
        """
        return self.amount if self.is_debit else None

    @property
    def credit(self) -> Optional[Amount]:
        """
        Returns the credit amount, if any.
        """
        return self.amount if self.is_credit else None


@dataclass
class Ledger(Generic[_T]):
    """
    Provides an account ledger model.
    """

    #: Account of the ledger.
    account: Account

    #: Initial balance of the ledger.
    initial: Balance

    #: Ledger entries.
    entries: List[LedgerEntry[_T]] = field(default_factory=list, init=False)

    @property
    def _last_balance(self) -> Quantity:
        """
        Returns the last balance.
        """
        try:
            return self.entries[-1].balance
        except IndexError:
            return self.initial.value

    def add(self, posting: Posting[_T]) -> LedgerEntry[_T]:
        """
        Adds a new ledger entry.

        :param posting: Posting the ledger entry is based on.
        :return: The new ledger entry.
        """
        ## Create the ledger entry.
        entry = LedgerEntry(self, posting, Quantity(self._last_balance + posting.amount * posting.direction.value))

        ## Add to the buffer:
        self.entries.append(entry)

        ## Done, return:
        return entry


@dataclass
class GeneralLedger(Generic[_T]):
    """
    Provides a general ledger model.
    """

    #: Opening date of the general ledger.
    opening: Date

    #: Closing date of the general ledger.
    closing: Date

    #: Individual account ledgers of the general ledger.
    ledgers: Dict[Account, Ledger[_T]]


def build_general_ledger(
    opening: Date, closing: Date, journal: Iterable[JournalEntry[_T]], initial: Dict[Account, Balance]
) -> GeneralLedger[_T]:
    """
    Builds a general ledger.

    :param opening: Opening date of the general ledger.
    :param closing: Closing date of the general ledger.
    :param journal: All available journal entries.
    :param initial: Opening balances for terminal accounts, if any.
    :return: A :py:class:`GeneralLedger` instance.
    """
    ## Initialize ledgers buffer as per available initial balances:
    ledgers: Dict[Account, Ledger[_T]] = {a: Ledger(a, b) for a, b in initial.items()}

    ## Iterate over journal postings and populate ledgers:
    for posting in (p for j in journal for p in j.postings if opening <= j.date <= closing):
        ## Get (or create) the ledger:
        ledger = ledgers.get(posting.account) or Ledger(posting.account, Balance(opening, Quantity(Decimal(0))))

        ## Add the posting to the ledger:
        ledger.add(posting)

    ## Done, return general ledger.
    return GeneralLedger(opening, closing, ledgers)
