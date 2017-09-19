from decimal import Decimal
from typing import Optional, Tuple, List

from abc import ABCMeta, abstractmethod

from .currencies import Currency
from .generic import Temporal, MaxPrecisionQuantizer


class FXRateLookupError(LookupError):
    """
    Provides an exception indicating that the foreign exchange rate is not found.
    """

    def __init__(self, ccy1: Currency, ccy2: Currency, asof: Temporal) -> None:
        """
        Initializes the foreign exchange rate lookup error.
        """
        ## Keep the slots:
        self.ccy1 = ccy1
        self.ccy2 = ccy2
        self.asof = asof

        ## Set the message:
        super().__init__(f"Foreign exchange rate for {ccy1}/{ccy2} not found as of {asof}")


class FXRate:
    """
    Defines a foreign exchange rate class.
    """

    ## Limit the slots.
    __slots__ = ["_ccy1", "_ccy2", "_asof", "_value"]

    def __init__(self, ccy1: Currency, ccy2: Currency, asof: Temporal, value: Decimal) -> None:
        """
        Initializes the foreign exchange rate class safely.

        :param ccy1: The first currency of the foreign exchange rate.
        :param ccy2: The second currency of the foreign exchange rate.
        :param asof: The temporal dimension value which the foreign exchange rate is effective asof.
        :param value: The value of the exchange rate (a :class:`Decimal` value other than ``0``).
        """
        ## Ensure that the value is not zero.
        if value.is_zero():
            ## Oops, we won't be able to proceed with this:
            raise ValueError(f"Foreign exchange rate value can not be zero: {ccy1}/{ccy2} as of {asof}.")

        ## Keep the first currency of the foreign exchange rate.
        self._ccy1: Currency = ccy1

        ## Keep the second currency of the foreign exchange rate.
        self._ccy2: Currency = ccy2

        ## Keep the temporal dimension of the foreign exchange rate.
        self._asof: Temporal = asof

        ## Keep the value of the foreign exchange rate.
        self._value: Decimal = value.quantize(MaxPrecisionQuantizer)

    @property
    def ccy1(self) -> Currency:
        """
        Returns the first currency of the rate.
        """
        return self._ccy1

    @property
    def ccy2(self) -> Currency:
        """
        Returns the second currency of the foreign exchange rate.
        """
        return self._ccy2

    @property
    def asof(self) -> Temporal:
        """
        Returns the temporal dimension value which the foreign exchange rate is effective as of.
        """
        return self._asof

    @property
    def value(self) -> Decimal:
        """
        Returns the value of the foreign exchange rate.
        """
        return self._value

    def __invert__(self) -> "FXRate":
        """
        Returns the inverted foreign exchange rate.
        """
        return FXRate(self.ccy2, self.ccy1, self.asof, self.value ** -1)


class FXRateService(metaclass=ABCMeta):
    """
    Provides an abstract class for serving foreign exchange rates.
    """

    #: Defines the default foreign exchange rate service for the runtime.
    default: Optional["FXRateService"] = None  # noqa: E704

    @abstractmethod
    def query(self, ccy1: Currency, ccy2: Currency, asof: Temporal, strict: bool=False) -> Optional[FXRate]:
        """
        Returns the foreign exchange rate of a given currency pair as of a given date.

        :param ccy1: The first currency of foreign exchange rate.
        :param ccy2: The second currency of foreign exchange rate.
        :param asof: Temporal dimension the foreign exchange rate is effective as of.
        :param strict: Indicates if we should raise a lookup error if that the foreign exchange rate can not be found.
        :return: The foreign exhange rate as a :class:`Decimal` instance or None.
        """
        pass

    @abstractmethod
    def queries(self, queries: List[Tuple[Currency, Currency, Temporal]], strict: bool=False) -> List[Optional[FXRate]]:
        """
        Returns foreign exchange rates for a given collection of currency pairs and dates.

        :param queries: An iterable of :class:`Currency`, :class:`Currency` and :class:`Temporal` tuples.
        :param strict: Indicates if we should raise a lookup error if that the foreign exchange rate can not be found.
        :return: An iterable of rates.
        """
        pass
