"""
This module defines common date/time typings and functions.
"""

__all__ = [
    "Date",
    "DateRange",
    "DateTime",
    "FinancialPeriods",
    "get_prev_weekday",
    "get_prev_year_end",
    "make_financial_periods",
    "now",
    "Time",
    "TimeDelta",
    "today",
    "tomorrow",
    "yesterday",
]

from calendar import isleap
from dataclasses import dataclass
from datetime import date as Date
from datetime import datetime as DateTime
from datetime import time as Time
from datetime import timedelta as TimeDelta
from typing import Dict, Iterator, Optional, OrderedDict

from pypara.commons.numbers import NaturalNumber, PositiveInteger


@dataclass(frozen=True)
class DateRange:
    """
    Provides an encoding for date ranges with inclusive date endpoints.

    A :py:class:`DateRange` is essentially a simple value object with two
    fields: :py:attr:`since` and :py:attr:`until`. These denote the start and
    end dates of the date range.

    Once successfully initialized, the value is guaranteed to have the property
    of :py:attr:`until` being equal to or greater than :py:attr:`since`.

    In an attempt to create a :py:class:`DateRange` instance that violates this
    condition, an :py:class:`AssertionError` is raised. In other words, the
    constructor of :py:meth:`DateRange.__init__` is unsafe. The safe alternative
    of creating :py:class:`DateRange` instances is :py:meth:`DateRange.of`. It
    returns a :py:class:`DateRange` instance if the condition is satisfied,
    ``None`` otherwise.

    Below are some examples of successful creation and erroneous attempt of
    creation:

    >>> good = DateRange(Date(2019, 1, 1), Date(2019, 1, 1))
    >>> good.since
    datetime.date(2019, 1, 1)
    >>> good.until
    datetime.date(2019, 1, 1)
    >>> list(good)
    [datetime.date(2019, 1, 1)]
    >>> better = DateRange(Date(2019, 1, 1), Date(2019, 1, 2))
    >>> better.since
    datetime.date(2019, 1, 1)
    >>> better.until
    datetime.date(2019, 1, 2)
    >>> list(better)
    [datetime.date(2019, 1, 1), datetime.date(2019, 1, 2)]
    >>> best = DateRange(Date(2019, 1, 1), Date(2019, 1, 3))
    >>> best.since
    datetime.date(2019, 1, 1)
    >>> best.until
    datetime.date(2019, 1, 3)
    >>> list(best)
    [datetime.date(2019, 1, 1), datetime.date(2019, 1, 2), datetime.date(2019, 1, 3)]

    In case of bad input:

    >>> bad = DateRange(Date(2019, 1, 2), Date(2019, 1, 1))
    Traceback (most recent call last):
    ...
        assert self.since > self.until
    AssertionError

    Therefore, it is advised to use :py:meth:`DateRange.of` instead:

    >>> DateRange.of(Date(2019, 1, 2), Date(2019, 1, 1)) is None
    True
    >>> DateRange.of(Date(2019, 1, 1), Date(2019, 1, 1))
    DateRange(since=datetime.date(2019, 1, 1), until=datetime.date(2019, 1, 1))
    """

    #: Date the range starts from (inclusive).
    since: Date

    #: Date the range ends on (inclusive).
    until: Date

    def __post_init__(self) -> None:
        """
        Checks whether the two date endpoints are consistent.

        :raises AssertError: If ``since`` is later than ``until``.
        """
        assert self.since <= self.until

    def __iter__(self) -> Iterator[Date]:
        """
        Returns an iterator for dates within the date-range in ascending order.

        :return: An :py:class:`typing.Iterator` of :py:class:`datetime.date` instances.
        """
        return iter((self.since + TimeDelta(days=i) for i in range(0, (self.until - self.since).days + 1)))

    @classmethod
    def of(cls, since: Date, until: Date) -> Optional["DateRange"]:
        """
        Safe, smart constructor to create :py:class:`DateRange` instances.

        :param since: Start date of the date range.
        :param until: End date of the date range.
        :return: A :py:class:`DateRange` instance if the ``since <= until`` is satisfied, ``None`` otherwise.

        >>> DateRange.of(Date(2019, 1, 2), Date(2019, 1, 1))
        >>> DateRange.of(Date(2019, 1, 1), Date(2019, 1, 1))
        DateRange(since=datetime.date(2019, 1, 1), until=datetime.date(2019, 1, 1))
        """
        return cls(since, until) if since <= until else None

    @classmethod
    def ordered(cls, date1: Date, date2: Date) -> "DateRange":
        """
        Safe, smart constructor to create :py:class:`DateRange` instances ensuring the order of dates.

        :param date1: First date.
        :param date2: Second date.
        :return: A :py:class:`DateRange` instance with ``(since, until)`` as ``(date1, date2)`` if ``date1 <= date2``
                 ``(date2, date1)`` otherwise.

        >>> DateRange.ordered(Date(2019, 1, 1), Date(2019, 1, 1))
        DateRange(since=datetime.date(2019, 1, 1), until=datetime.date(2019, 1, 1))
        >>> DateRange.ordered(Date(2019, 1, 1), Date(2019, 1, 2))
        DateRange(since=datetime.date(2019, 1, 1), until=datetime.date(2019, 1, 2))
        >>> DateRange.ordered(Date(2019, 1, 2), Date(2019, 1, 1))
        DateRange(since=datetime.date(2019, 1, 1), until=datetime.date(2019, 1, 2))
        """
        return cls(date1, date2) if date1 <= date2 else cls(date2, date1)

    @classmethod
    def pivotal(cls, pivot: Date, prev: NaturalNumber, next: NaturalNumber) -> "DateRange":
        """
        Creates a :py:class:`DateRange` as per given ``pivot`` date in time to create date range since ``prev`` years
        back and ``next`` years forward.

        :param pivot: Pivot date in time.
        :param prev: Numbers to go back in years.
        :param next: Numbers to go forward in years.
        :return: A :py:class:`DateRange` instance.

        >>> DateRange.pivotal(Date(2019, 12, 31), NaturalNumber(0), NaturalNumber(0))
        DateRange(since=datetime.date(2019, 12, 31), until=datetime.date(2019, 12, 31))
        >>> DateRange.pivotal(Date(2019, 12, 31), NaturalNumber(0), NaturalNumber(1))
        DateRange(since=datetime.date(2019, 12, 31), until=datetime.date(2020, 12, 31))
        >>> DateRange.pivotal(Date(2019, 12, 31), NaturalNumber(1), NaturalNumber(0))
        DateRange(since=datetime.date(2018, 12, 31), until=datetime.date(2019, 12, 31))
        >>> DateRange.pivotal(Date(2019, 12, 31), NaturalNumber(1), NaturalNumber(1))
        DateRange(since=datetime.date(2018, 12, 31), until=datetime.date(2020, 12, 31))
        >>> DateRange.pivotal(Date(2020, 2, 29), NaturalNumber(0), NaturalNumber(0))
        DateRange(since=datetime.date(2020, 2, 29), until=datetime.date(2020, 2, 29))
        >>> DateRange.pivotal(Date(2020, 2, 29), NaturalNumber(0), NaturalNumber(1))
        DateRange(since=datetime.date(2020, 2, 29), until=datetime.date(2021, 2, 28))
        >>> DateRange.pivotal(Date(2020, 2, 29), NaturalNumber(1), NaturalNumber(0))
        DateRange(since=datetime.date(2019, 2, 28), until=datetime.date(2020, 2, 29))
        >>> DateRange.pivotal(Date(2020, 2, 29), NaturalNumber(1), NaturalNumber(1))
        DateRange(since=datetime.date(2019, 2, 28), until=datetime.date(2021, 2, 28))
        """
        ## Get the target since date:
        sy, sm, sd = pivot.year - prev, pivot.month, pivot.day

        ## Check if (m, d) is a valid one:
        if not isleap(sy) and sm == 2 and sd == 29:
            sd = 28

        ## Get the target until date:
        uy, um, ud = pivot.year + next, pivot.month, pivot.day

        ## Check if (m, d) is a valid one:
        if not isleap(uy) and um == 2 and ud == 29:
            ud = 28

        ## Create the date range and return:
        return cls(Date(sy, sm, sd), Date(uy, um, ud))

    @classmethod
    def dtd(cls, date: Date) -> "DateRange":
        """
        Returns day-to-date date range as of the given date.

        :param date: To-date.
        :return: Day-to-date (DTD) date range.

        >>> DateRange.dtd(Date(2019, 1, 9))
        DateRange(since=datetime.date(2019, 1, 9), until=datetime.date(2019, 1, 9))
        >>> DateRange.dtd(Date(2020, 3, 1))
        DateRange(since=datetime.date(2020, 3, 1), until=datetime.date(2020, 3, 1))
        >>> DateRange.dtd(Date(2020, 3, 9))
        DateRange(since=datetime.date(2020, 3, 9), until=datetime.date(2020, 3, 9))
        """
        return cls(date, date)

    @classmethod
    def mtd(cls, date: Date) -> "DateRange":
        """
        Returns month-to-date date range as of the given date.

        :param date: To-date.
        :return: Month-to-date (MTD) date range.

        >>> DateRange.mtd(Date(2019, 1, 9))
        DateRange(since=datetime.date(2019, 1, 1), until=datetime.date(2019, 1, 9))
        >>> DateRange.mtd(Date(2020, 3, 1))
        DateRange(since=datetime.date(2020, 3, 1), until=datetime.date(2020, 3, 1))
        >>> DateRange.mtd(Date(2020, 3, 9))
        DateRange(since=datetime.date(2020, 3, 1), until=datetime.date(2020, 3, 9))
        """
        return cls(date.replace(day=1), date)

    @classmethod
    def ytd(cls, date: Date) -> "DateRange":
        """
        Returns year-to-date date range as of the given date.

        :param date: To-date.
        :return: Year-to-date (YTD) date range.

        >>> DateRange.ytd(Date(2020, 1, 1))
        DateRange(since=datetime.date(2020, 1, 1), until=datetime.date(2020, 1, 1))
        >>> DateRange.ytd(Date(2019, 1, 9))
        DateRange(since=datetime.date(2019, 1, 1), until=datetime.date(2019, 1, 9))
        >>> DateRange.ytd(Date(2020, 3, 1))
        DateRange(since=datetime.date(2020, 1, 1), until=datetime.date(2020, 3, 1))
        """
        return cls(date.replace(month=1, day=1), date)

    @classmethod
    def year(cls, year: PositiveInteger) -> "DateRange":
        """
        Returns a full year date range for the given year.

        :param year: The year.
        :return: Year date range.

        >>> DateRange.year(PositiveInteger(2019))
        DateRange(since=datetime.date(2019, 1, 1), until=datetime.date(2019, 12, 31))
        >>> DateRange.year(PositiveInteger(2020))
        DateRange(since=datetime.date(2020, 1, 1), until=datetime.date(2020, 12, 31))
        """
        return cls(Date(year, 1, 1), Date(year, 12, 31))

    @classmethod
    def cover(cls, first: "DateRange", *rest: "DateRange") -> "DateRange":
        """
        Returns the date-range that covers all given date ranges.

        :param first: First date range.
        :param rest: Rest of date ranges.
        :return: A new date range which covers all given date ranges.

        >>> DateRange.cover(DateRange.dtd(Date(2019, 4, 1)), DateRange.mtd(Date(2020, 2, 29)), DateRange.ytd(Date(2018, 3, 6)))  # noqa: E501
        DateRange(since=datetime.date(2018, 1, 1), until=datetime.date(2020, 2, 29))
        """
        return DateRange(min(first, *rest, key=lambda x: x.since).since, max(first, *rest, key=lambda x: x.until).until)

    def since_prev_year_end(self, years: PositiveInteger = PositiveInteger(1), weekday: bool = False) -> "DateRange":
        """
        Re-creates the date range starting from the previous ``years`` number of
        years as per :py:attr:`DateRange.since`.

        >>> DateRange(Date(2019, 12, 31), Date(2019, 12, 31)).since_prev_year_end(PositiveInteger(1))
        DateRange(since=datetime.date(2018, 12, 31), until=datetime.date(2019, 12, 31))
        >>> DateRange(Date(2019, 12, 30), Date(2019, 12, 31)).since_prev_year_end(PositiveInteger(1))
        DateRange(since=datetime.date(2018, 12, 31), until=datetime.date(2019, 12, 31))
        >>> DateRange(Date(2019, 12, 30), Date(2019, 12, 31)).since_prev_year_end(PositiveInteger(2))
        DateRange(since=datetime.date(2017, 12, 31), until=datetime.date(2019, 12, 31))
        >>> DateRange(Date(2019, 12, 31), Date(2019, 12, 31)).since_prev_year_end(PositiveInteger(1), True)
        DateRange(since=datetime.date(2018, 12, 31), until=datetime.date(2019, 12, 31))
        >>> DateRange(Date(2019, 12, 30), Date(2019, 12, 31)).since_prev_year_end(PositiveInteger(1), True)
        DateRange(since=datetime.date(2018, 12, 31), until=datetime.date(2019, 12, 31))
        >>> DateRange(Date(2019, 12, 30), Date(2019, 12, 31)).since_prev_year_end(PositiveInteger(2), True)
        DateRange(since=datetime.date(2017, 12, 29), until=datetime.date(2019, 12, 31))

        :param years: Number of years to go back as a positive integer.
        :param weekday: Indicates if we want the year end to be a weekday.
        :return: A new :py:class:`DateRange` instance.
        """
        ## Get the year end as requested:
        yearend = get_prev_year_end(self.since, years)

        ## Create the new date range and return:
        return DateRange(get_prev_weekday(yearend) if weekday and yearend.weekday() in {5, 6} else yearend, self.until)


#: Defines a custom financial periods container.
FinancialPeriods = Dict[str, DateRange]


def make_financial_periods(date: Date, lookback: PositiveInteger) -> FinancialPeriods:
    """
    Creates financial periods for the given date with ``lookback`` number of years.

    :param date: Date to create financial periods for.
    :param lookback: A positive integer describing the number of years to go back.
    :return: A dictionary of financial period label and date range for the financual period.

    >>> sorted(make_financial_periods(Date(2019, 1, 10), PositiveInteger(1)).keys())
    ['2018', 'DTD', 'MTD', 'YTD']
    >>> sorted(make_financial_periods(Date(2019, 1, 10), PositiveInteger(2)).keys())
    ['2017', '2018', 'DTD', 'MTD', 'YTD']
    >>> sorted(make_financial_periods(Date(2019, 1, 10), PositiveInteger(3)).keys())
    ['2016', '2017', '2018', 'DTD', 'MTD', 'YTD']
    >>> sorted(make_financial_periods(Date(2020, 2, 29), PositiveInteger(3)).keys())
    ['2017', '2018', '2019', 'DTD', 'MTD', 'YTD']
    >>> periods = make_financial_periods(Date(2020, 2, 29), PositiveInteger(3))
    >>> periods["DTD"]
    DateRange(since=datetime.date(2020, 2, 29), until=datetime.date(2020, 2, 29))
    >>> periods["MTD"]
    DateRange(since=datetime.date(2020, 2, 1), until=datetime.date(2020, 2, 29))
    >>> periods["YTD"]
    DateRange(since=datetime.date(2020, 1, 1), until=datetime.date(2020, 2, 29))
    >>> periods["2019"]
    DateRange(since=datetime.date(2019, 1, 1), until=datetime.date(2019, 12, 31))
    >>> periods["2018"]
    DateRange(since=datetime.date(2018, 1, 1), until=datetime.date(2018, 12, 31))
    >>> periods["2017"]
    DateRange(since=datetime.date(2017, 1, 1), until=datetime.date(2017, 12, 31))
    """
    ## Get years iterable:
    years = (date.year - i for i in range(1, lookback + 1) if i <= date.year)

    ## Build ranges and return:
    return OrderedDict(
        (
            ("DTD", DateRange.dtd(date)),
            ("MTD", DateRange.mtd(date)),
            ("YTD", DateRange.ytd(date)),
            *((f"{y}", DateRange.year(PositiveInteger(y))) for y in years),
        )
    )


def now(**kwargs: int) -> DateTime:
    """
    Returns the current date/time with replacements if provided.

    >>> now(year=1981, month=8, day=27, hour=18, minute=19, second=20, microsecond=1)
    datetime.datetime(1981, 8, 27, 18, 19, 20, 1)
    """
    return DateTime.now().replace(**kwargs)  # type: ignore


def today(**kwargs: int) -> Date:
    """
    Returns the current date with replacements if provided.

    >>> today(year=1981, month=8, day=27)
    datetime.date(1981, 8, 27)
    """
    return Date.today().replace(**kwargs)


def yesterday(x: Optional[Date] = None) -> Date:
    """
    Returns yesterday as of given (optional) date.

    >>> yesterday() == today() - TimeDelta(days=1)
    True
    >>> yesterday(Date(2019, 1, 1))
    datetime.date(2018, 12, 31)
    """
    return (x or today()) - TimeDelta(days=1)


def tomorrow(x: Optional[Date] = None) -> Date:
    """
    Returns tomorrow as of given (optional) date.

    >>> tomorrow() == today() + TimeDelta(days=1)
    True
    >>> tomorrow(Date(2018, 12, 31))
    datetime.date(2019, 1, 1)
    """
    return (x or today()) + TimeDelta(days=1)


def get_prev_weekday(x: Optional[Date] = None) -> Date:
    """
    Returns the previous week day as of given (optional) date.

    :param x: Optional date in time.
    :return: Previous business day.

    >>> get_prev_weekday(Date(2020, 1, 1))
    datetime.date(2019, 12, 31)
    >>> get_prev_weekday(Date(2020, 1, 2))
    datetime.date(2020, 1, 1)
    >>> get_prev_weekday(Date(2020, 1, 3))
    datetime.date(2020, 1, 2)
    >>> get_prev_weekday(Date(2020, 1, 4))
    datetime.date(2020, 1, 3)
    >>> get_prev_weekday(Date(2020, 1, 5))
    datetime.date(2020, 1, 3)
    >>> get_prev_weekday(Date(2020, 1, 6))
    datetime.date(2020, 1, 3)
    >>> get_prev_weekday(Date(2020, 1, 7))
    datetime.date(2020, 1, 6)
    """
    ## Get the day:
    x = x or today()

    ## Define the offset:
    offset = max(1, (x.weekday() + 6) % 7 - 3)

    ## Compute the day and return:
    return x - TimeDelta(days=offset)


def get_prev_year_end(x: Optional[Date] = None, years: PositiveInteger = PositiveInteger(1)) -> Date:
    """
    Returns the year end of the previous year as of given (optional) date.

    >>> get_prev_year_end() == Date(today().year - 1, 12, 31)
    True
    >>> get_prev_year_end(Date(2019, 1, 1))
    datetime.date(2018, 12, 31)
    >>> get_prev_year_end(Date(2018, 12, 31))
    datetime.date(2017, 12, 31)
    >>> get_prev_year_end(Date(2018, 12, 31), PositiveInteger(2))
    datetime.date(2016, 12, 31)
    """
    return Date((x or today()).year - years, 12, 31)
