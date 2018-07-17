import calendar
import datetime
from decimal import Decimal
from typing import Dict, Callable, Set, Optional, List, Iterable, NamedTuple

from pypara.currencies import Currency, Currencies
from pypara.generic import Date
from pypara.monetary import Money

#: Defines a type alias for day count fraction calculation functions.
DCFC = Callable[[Date, Date, Date], Decimal]


def _as_ccys(codes: Set[str]) -> Set[Currency]:
    """
    Converts a set of currency codes to a set of currencies.
    """
    return {Currencies[c] for c in codes}


def _get_date_range(start: Date, end: Date) -> Iterable[Date]:
    """
    Returns a generator of dates falling into range within the given period (``end`` is exclusive).

    :param start: The start date of the period.
    :param end: The end date of the period.
    :return: A generator of dates.
    """
    for i in range((end - start).days):
        yield start + datetime.timedelta(days=i)


def _get_actual_day_count(start: Date, end: Date) -> int:
    """
    Counts the actual number of days in the given period.

    :param start: The start date of the period.
    :param end: The end date of the period.
    :return: The number of days in the given period.

    >>> _get_actual_day_count(datetime.date(2017, 1, 1), datetime.date(2017, 1, 1))
    0
    >>> _get_actual_day_count(datetime.date(2017, 1, 1), datetime.date(2017, 1, 2))
    1
    """
    return (end - start).days


def _has_leap_day(start: Date, end: Date) -> bool:
    """
    Indicates if the range has any leap day.
    """
    ## Get all leap years:
    years = {year for year in range(start.year, end.year + 1) if calendar.isleap(year)}

    ## Check if any of the lap day falls in our range:
    for year in years:
        ## Construct the leap day:
        leapday = datetime.date(year, 2, 29)

        ## Is the leap date in the range?
        if start <= leapday <= end:
            ## Yes, the leap day is within the date range. Return True:
            return True

    ## No leap day in the range, return False:
    return False


def _is_last_day_of_month(date: Date) -> bool:
    """
    Indicates if the date is the last day of the month.
    """
    return date.day == calendar.monthrange(date.year, date.month)[1]


class DCC(NamedTuple):
    """
    Defines a day count convention model.
    """

    #: Defines the name of the day count convention.
    name: str

    #: Defines a set of alternative names of the day count convention.
    altnames: Set[str]

    #: Defines a set of currencies which are known to use this convention by default.
    currencies: Set[Currency]

    #: Defines the day count fraction calculation function.
    calculate_fraction: DCFC

    def __call__(self, principal: Money, rate: Decimal, start: Date, asof: Date, end: Optional[Date]=None) -> Money:
        """
        Calculates the interest for the given schedule.
        """
        return principal * rate * self[3](start, asof, end or asof)


class DCCRegistryMachinery:
    """
    Provides the day count registry model.

    >>> principal = Money.of(Currencies["USD"], Decimal(1000000), datetime.date.today())
    >>> start = datetime.date(2007, 12, 28)
    >>> end = datetime.date(2008, 2, 28)
    >>> rate = Decimal(0.01)
    >>> dcc = DCCRegistry.find("Act/Act")
    >>> round(dcc.calculate_fraction(start, end, end), 14)
    Decimal('0.16942884946478')
    >>> dcc(principal, rate, start, end).qty
    Decimal('1694.29')
    """

    def __init__(self) -> None:
        """
        Initializes the registry.
        """
        ## Define the main registry buffer:
        self._buffer_main: Dict[str, DCC] = {}

        ## Defines the registry buffer for alternative DCC names:
        self._buffer_altn: Dict[str, DCC] = {}

    def _is_registered(self, name: str) -> bool:
        """
        Checks if the given name is ever registered before.
        """
        return name in self._buffer_main or name in self._buffer_altn

    def register(self, dcc: DCC) -> None:
        """
        Attempts to register the given day count convention.
        """
        ## Check if the main name is ever registered before:
        if self._is_registered(dcc.name):
            ## Yep, raise a TypeError:
            raise TypeError(f"Day count convention '{dcc.name}' is already registered")

        ## Add to the main buffer:
        self._buffer_main[dcc.name] = dcc

        ## Check if there is any registry conflict:
        for name in dcc.altnames:
            ## Check if the name is ever registered:
            if self._is_registered(name):
                ## Yep, raise a TypeError:
                raise TypeError(f"Day count convention '{dcc.name}' is already registered")

            ## Register to the alternative buffer:
            self._buffer_altn[name] = dcc

    def _find_strict(self, name: str) -> Optional[DCC]:
        """
        Attempts to find the day count convention by the given name.
        """
        return self._buffer_main.get(name) or self._buffer_altn.get(name)

    def find(self, name: str) -> Optional[DCC]:
        """
        Attempts to find the day count convention by the given name.

        Note that all day count conventions are registered under stripped, uppercased names. Therefore,
        the implementation will first attempt to find by given name as is. If it can not find it, it will
        strip and uppercase the name and try to find it as such as a last resort.
        """
        return self._find_strict(name) or self._find_strict(name.strip().upper())


#: Defines the default DCC registry.
DCCRegistry = DCCRegistryMachinery()


def dcc(name: str, altnames: Optional[Set[str]]=None, ccys: Optional[Set[Currency]]=None) -> Callable[[DCFC], DCFC]:
    """
    Registers a day count fraction calculator under the given names and alternative names (if any).

    :param name: The name of the day count convention.
    :param altnames: A set of alternative names of the day count convention, if any.
    :param ccys: A set of currencies which are known to use this convention by default, if any.
    :return: Registered day count fraction calculation function.
    """
    def register_and_return_dcfc(func: DCFC) -> DCFC:
        """
        Registers the given day count fraction calculator and returns it.

        :param func: Day count fraction calculation function to be registered.
        :return: Registered day count fraction calculation function.
        """
        ## Create the DCC instance:
        dcc = DCC(name, altnames or set([]), ccys or set([]), func)

        ## Attempt to register the DCC:
        DCCRegistry.register(dcc)

        ## Attach the dcc instance to the day count fraction calculation function (for whatever it is worth):
        setattr(func, "__dcc", dcc)

        ## Done, return the function (if above statment did not raise any exceptions):
        return func
    return register_and_return_dcfc


@dcc("Act/Act", {"Actual/Actual", "Actual/Actual (ISDA)"})
def dcfc_act_act(start: Date, asof: Date, end: Date) -> Decimal:
    """
    Computes the day count fraction for "Act/Act" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_act_act(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16942884946478')
    >>> round(dcfc_act_act(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.17216108990194')
    >>> round(dcfc_act_act(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08243131970956')
    >>> round(dcfc_act_act(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.32625945055768')
    """
    ## Get all years of interest by checking the leap year:
    years = {year: calendar.isleap(year) for year in range(start.year, asof.year + 1)}

    ## Define the buffer of days for the day count. The former is for non-leap years, the latter for leap years:
    buffer: List[int] = [0, 0]

    ## Iterate over the date range and count:
    for date in _get_date_range(start, asof):
        ## Check the year and modify buffer accordingly:
        if years[date.year]:
            ## Yep, it is a leap year:
            buffer[1] += 1
        else:
            ## Nope, not a leap year:
            buffer[0] += 1

    ## Done, compute and return:
    return Decimal(buffer[0]) / Decimal(365) + Decimal(buffer[1]) / Decimal(366)


@dcc("Act/360", {"Actual/360", "French", "360"},
     _as_ccys({"AUD", "CAD", "CHF", "EUR", "USD", "DKK", "CZK", "HUF", "SEK", "IDR", "NOK", "JPY", "NZD", "THB"}))
def dcfc_act_360(start: Date, asof: Date, end: Date) -> Decimal:
    """
    Computes the day count fraction for "Act/360" convention.

    :param start: The start date of the period.
    :param end: The end date of the period.
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_act_360(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.17222222222222')
    >>> round(dcfc_act_360(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.17500000000000')
    >>> round(dcfc_act_360(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.10000000000000')
    >>> round(dcfc_act_360(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.34722222222222')
    """
    return _get_actual_day_count(start, asof) / Decimal(360)


@dcc("Act/365F", {"Actual/365 Fixed", "English", "365"}, _as_ccys({"GBP", "HKD", "INR", "PLN", "SGD", "ZAR", "MYR"}))
def dcfc_act_365_f(start: Date, asof: Date, end: Date) -> Decimal:
    """
    Computes the day count fraction for the "Act/365F" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_act_365_f(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16986301369863')
    >>> round(dcfc_act_365_f(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.17260273972603')
    >>> round(dcfc_act_365_f(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08493150684932')
    >>> round(dcfc_act_365_f(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.32876712328767')
    """
    return _get_actual_day_count(start, asof) / Decimal(365)


@dcc("Act/365A", {"Actual/365 Actual"})
def dcfc_act_365_a(start: Date, asof: Date, end: Date) -> Decimal:
    """
    Computes the day count fraction for the "Act/365A" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_act_365_a(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16986301369863')
    >>> round(dcfc_act_365_a(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.17213114754098')
    >>> round(dcfc_act_365_a(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08196721311475')
    >>> round(dcfc_act_365_a(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.32513661202186')
    """
    return _get_actual_day_count(start, asof) / Decimal(366 if _has_leap_day(start, asof) else 365)


@dcc("Act/365L", {"Actual/365 Leap Year"})
def dcfc_act_365_l(start: Date, asof: Date, end: Date) -> Decimal:
    """
    Computes the day count fraction for the "Act/365L" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_act_365_l(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16939890710383')
    >>> round(dcfc_act_365_l(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.17213114754098')
    >>> round(dcfc_act_365_l(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08196721311475')
    >>> round(dcfc_act_365_l(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.32876712328767')
    """
    return _get_actual_day_count(start, asof) / Decimal(366 if calendar.isleap(asof.year) else 365)


@dcc("NL/365", {"Actual/365 No Leap Year", "NL365"})
def dcfc_nl_365(start: Date, asof: Date, end: Date) -> Decimal:
    """
    Computes the day count fraction for the "NL/365" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_nl_365(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16986301369863')
    >>> round(dcfc_nl_365(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16986301369863')
    >>> round(dcfc_nl_365(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08219178082192')
    >>> round(dcfc_nl_365(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.32602739726027')
    """
    return (_get_actual_day_count(start, asof) - (1 if _has_leap_day(start, asof) else 0)) / Decimal(365)


@dcc("30/360 ISDA", {"30/360 US Municipal", "Bond Basis"})
def dcfc_30_360_isda(start: Date, asof: Date, end: Date) -> Decimal:
    """
    Computes the day count fraction for the "30/360 ISDA" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_30_360_isda(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16666666666667')
    >>> round(dcfc_30_360_isda(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16944444444444')
    >>> round(dcfc_30_360_isda(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08333333333333')
    >>> round(dcfc_30_360_isda(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.33333333333333')
    """
    ## Get the new start date, if required:
    if start.day == 31:
        start = datetime.date(start.year, start.month, 30)

    ## Get the new asof date, if required:
    if start.day == 30 and asof.day == 31:
        asof = datetime.date(asof.year, asof.month, 30)

    ## Compute number of days:
    nod = (asof.day - start.day) + 30 * (asof.month - start.month) + 360 * (asof.year - start.year)

    ## Done, compute and return the day count fraction:
    return nod / Decimal(360)


@dcc("30E/360", {"30/360 ISMA", "30/360 European", "30S/360 Special German", "Eurobond Basis"})
def dcfc_30_e_360(start: Date, asof: Date, end: Date) -> Decimal:
    """
    Computes the day count fraction for the "30E/360" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_30_e_360(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16666666666667')
    >>> round(dcfc_30_e_360(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16944444444444')
    >>> round(dcfc_30_e_360(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08333333333333')
    >>> round(dcfc_30_e_360(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.33055555555556')
    """
    ## Get the new start date, if required:
    if start.day == 31:
        start = datetime.date(start.year, start.month, 30)

    ## Get the new asof date, if required:
    if asof.day == 31:
        asof = datetime.date(asof.year, asof.month, 30)

    ## Compute number of days:
    nod = (asof.day - start.day) + 30 * (asof.month - start.month) + 360 * (asof.year - start.year)

    ## Done, compute and return the day count fraction:
    return nod / Decimal(360)


@dcc("30E+/360")
def dcfc_30_e_plus_360(start: Date, asof: Date, end: Date) -> Decimal:
    """
    Computes the day count fraction for the "30E+/360" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.


    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_30_e_plus_360(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16666666666667')
    >>> round(dcfc_30_e_plus_360(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16944444444444')
    >>> round(dcfc_30_e_plus_360(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08333333333333')
    >>> round(dcfc_30_e_plus_360(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.33333333333333')
    """
    ## Get the new start date, if required:
    if start.day == 31:
        start = datetime.date(start.year, start.month, 30)

    ## Get the new asof date, if required:
    if asof.day == 31:
        asof = asof + datetime.timedelta(days=1)

    ## Compute number of days:
    nod = (asof.day - start.day) + 30 * (asof.month - start.month) + 360 * (asof.year - start.year)

    ## Done, compute and return the day count fraction:
    return nod / Decimal(360)


@dcc("30/360 German", {"30E/360 ISDA"})
def dcfc_30_360_german(start: Date, asof: Date, end: Date) -> Decimal:
    """
    Computes the day count fraction.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_30_360_german(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16666666666667')
    >>> round(dcfc_30_360_german(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16944444444444')
    >>> round(dcfc_30_360_german(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08333333333333')
    >>> round(dcfc_30_360_german(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.33055555555556')
    """
    ## Get the new start date, if required:
    if start.day == 31 or (start.month == 2 and _is_last_day_of_month(start)):
        d1 = 30
    else:
        d1 = start.day

    ## Get the new asof date, if required:
    if asof.day == 31 or (asof.month == 2 and _is_last_day_of_month(asof) and end != asof):
        d2 = 30
    else:
        d2 = asof.day

    ## Compute number of days:
    nod = (d2 - d1) + 30 * (asof.month - start.month) + 360 * (asof.year - start.year)

    ## Done, compute and return the day count fraction:
    return nod / Decimal(360)


@dcc("30/360 US", {"30U/360", "30US/360"})
def dcfc_30_360_us(start: Date, asof: Date, end: Date) -> Decimal:
    """
    Computes the day count fraction for the "30/360 US" convention.

    :param start: The start date of the period.
    :param asof: The date which the day count fraction to be calculated as of.
    :param end: The end date of the period (a.k.a. termination date).
    :return: Day count fraction.

    >>> ex1_start, ex1_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 28)
    >>> ex2_start, ex2_asof = datetime.date(2007, 12, 28), datetime.date(2008, 2, 29)
    >>> ex3_start, ex3_asof = datetime.date(2007, 10, 31), datetime.date(2008, 11, 30)
    >>> ex4_start, ex4_asof = datetime.date(2008, 2, 1), datetime.date(2009, 5, 31)
    >>> round(dcfc_30_360_us(start=ex1_start, asof=ex1_asof, end=ex1_asof), 14)
    Decimal('0.16666666666667')
    >>> round(dcfc_30_360_us(start=ex2_start, asof=ex2_asof, end=ex2_asof), 14)
    Decimal('0.16944444444444')
    >>> round(dcfc_30_360_us(start=ex3_start, asof=ex3_asof, end=ex3_asof), 14)
    Decimal('1.08333333333333')
    >>> round(dcfc_30_360_us(start=ex4_start, asof=ex4_asof, end=ex4_asof), 14)
    Decimal('1.33333333333333')
    """
    ## Get D1 and D2:
    d1 = start.day
    d2 = asof.day

    ## Need to change D1?
    if _is_last_day_of_month(start):
        ## Yep, change it:
        d1 = 30

        ## Shall we change the d2, too?
        if _is_last_day_of_month(asof):
            d2 = 30

    ## Revisit d2:
    if d2 == 31 and (d1 == 30 or d1 == 31):
        d2 = 30

    ## Revisit d1:
    if d1 == 31:
        d1 = 30

    ## Compute number of days:
    nod = (d2 - d1) + 30 * (asof.month - start.month) + 360 * (asof.year - start.year)

    ## Done, return:
    return nod / Decimal(360)
