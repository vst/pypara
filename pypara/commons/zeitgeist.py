"""
This module defines common date/time typings and functions.
"""

__all__ = ["Date", "DateTime", "TimeDelta", "DateRange"]

import datetime
from dataclasses import dataclass
from datetime import date as Date
from datetime import datetime as DateTime
from datetime import timedelta as TimeDelta


@dataclass(frozen=True)
class DateRange:
    """
    Provides an encoding for date ranges.
    """

    #: Date the range starts from (inclusive).
    since: datetime.date

    #: Date the range ends on (inclusive).
    until: datetime.date
