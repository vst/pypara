from collections import namedtuple
from decimal import Decimal
from typing import SupportsAbs, SupportsFloat, SupportsInt, SupportsRound, TypeVar, Generic, Any, Union, Optional

from pypara.currencies import Currency
from pypara.exchange import FXRateService, FXRateLookupError
from pypara.generic import Date, ProgrammingError

#: Defines the self type (sic.) for the monetary value implementations.
MV = TypeVar("MV", bound="MonetaryValue")


class MonetaryValue(Generic[MV], SupportsAbs[MV], SupportsFloat, SupportsInt, SupportsRound[MV]):
    """
    Provides an abstract monetary value model and its semantics.
    """

    ## No need for slots.
    __slots__ = ()

    ccy: Currency

    qty: Decimal

    dov: Date

    defined: bool  # noqa: E704

    undefined: bool

    def __bool__(self: MV) -> bool:
        """
        Returns the logical representation of the monetary value object.

        A monetary value object is:

        1. ``True`` if (a) it is *defined* **and** (b) it's quantity is non-zero.
        2. ``False`` otherwise.
        """
        raise NotImplementedError

    def __eq__(self: MV, other: Any) -> bool:
        """
        Checks the equality of two monetary value instances.
        """
        raise NotImplementedError

    def __abs__(self: MV) -> MV:
        """
        Returns the absolute monetary value if *defined*, itself otherwise.
        """
        raise NotImplementedError

    def __float__(self: MV) -> float:
        """
        Returns the quantity as a ``float`` if *defined*, raises class:`MonetaryOperationException` otherwise.
        """
        raise NotImplementedError

    def __int__(self: MV) -> int:
        """
        Returns the quantity as an ``int`` if *defined*, raises class:`MonetaryOperationException` otherwise.
        """
        raise NotImplementedError

    def __round__(self: MV, ndigits: int = 0) -> MV:
        """
        Rounds the quantity of the monetary value to ``ndigits`` by using ``HALF_EVEN`` method if *defined*, itself
        otherwise.
        """
        raise NotImplementedError

    def __neg__(self: MV) -> MV:
        """
        Negates the quantity of the monetary value if *defined*, itself otherwise.
        """
        raise NotImplementedError

    def __pos__(self: MV) -> MV:
        """
        Returns same monetary value if *defined*, itself otherwise.
        """
        raise NotImplementedError

    def __mul__(self: MV, other: Union[Decimal, int, float]) -> MV:
        """
        Multiplies the quantity by the given number if *defined*, itself otherwise.
        """
        raise NotImplementedError

    def __truediv__(self: MV, other: Union[Decimal, int, float]) -> MV:
        """
        Applies ordinary division on the quantity if *defined*, itself otherwise.
        """
        raise NotImplementedError

    def __floordiv__(self: MV, other: Union[Decimal, int, float]) -> MV:
        """
        Applies *floor* division on the quantity if *defined*, itself otherwise.
        """
        raise NotImplementedError

    def __add__(self: MV, other: Union[MV, Decimal, int, float]) -> MV:
        """
        Applies addition on the quantity if *defined*, raises class:`MonetaryOperationException` if other is not a
        monetary value.

        If `other` is a :class:`MonetaryValue` instance of self-type:

        1. Returns other if self is undefined,
        2. Returns itself if `other` is undefined,
        3. Raises :class:`IncompatibleCurrencyError` if currencies do not match.
        """
        raise NotImplementedError

    def __sub__(self: MV, other: Union[MV, Decimal, int, float]) -> MV:
        """
        Applies addition on the quantity if *defined*, raises class:`MonetaryOperationException` if other is not a
        monetary value.

        If `other` is a :class:`MonetaryValue` instance of self-type:

        1. Returns other if self is undefined,
        2. Returns itself if ``other`` is undefined,
        3. Raises :class:`IncompatibleCurrencyError` if currencies do not match.
        """
        raise NotImplementedError

    def __lt__(self: MV, other: MV) -> bool:
        """
        Applies "less than" comparison against ``other``.

        If ``self`` is undefined::
        1. Return ``True`` if ``other`` is defined.
        2. Return ``False`` if ``other`` is undefined.

        If ``other`` is undefined::
        1. Return ``False`` if ``self`` is defined.
        2. Return ``False`` if ``self`` is undefined.

        If both ``self`` and ``other`` are defined:
        1. Raise :class:`IncompatibleCurrencyError` if currencies do not match,
        2. Return ``True`` or ``False`` depending on the quantity of the monetary value.
        """
        raise NotImplementedError

    def __le__(self: MV, other: MV) -> bool:
        """
        Applies "less than or equal to" comparison against ``other``.

        If ``self`` is undefined::
        1. Return ``True`` if ``other`` is defined.
        2. Return ``True`` if ``other`` is undefined.

        If ``other`` is undefined::
        1. Return ``False`` if ``self`` is defined.
        2. Return ``True`` if ``self`` is undefined.

        If both ``self`` and ``other`` are defined:
        1. Raise :class:`IncompatibleCurrencyError` if currencies do not match,
        2. Return ``True`` or ``False`` depending on the quantity of the monetary value.
        """
        raise NotImplementedError

    def __gt__(self: MV, other: MV) -> bool:
        """
        Applies "greater than" comparison against ``other``.

        If ``self`` is undefined::
        1. Return ``False`` if ``other`` is defined.
        2. Return ``False`` if ``other`` is undefined.

        If ``other`` is undefined::
        1. Return ``True`` if ``self`` is defined.
        2. Return ``False`` if ``self`` is undefined.

        If both ``self`` and ``other`` are defined:
        1. Raise :class:`IncompatibleCurrencyError` if currencies do not match,
        2. Return ``True`` or ``False`` depending on the quantity of the monetary value.
        """
        raise NotImplementedError

    def __ge__(self: MV, other: MV) -> bool:
        """
        Applies "greater than or equal to" comparison against ``other``.

        If ``self`` is undefined::
        1. Return ``False`` if ``other`` is defined.
        2. Return ``True`` if ``other`` is undefined.

        If ``other`` is undefined::
        1. Return ``True`` if ``self`` is defined.
        2. Return ``True`` if ``self`` is undefined.

        If both ``self`` and ``other`` are defined:
        1. Raise :class:`IncompatibleCurrencyError` if currencies do not match,
        2. Return ``True`` or ``False`` depending on the quantity of the monetary value.
        """
        raise NotImplementedError

    def with_ccy(self: MV, ccy: Currency) -> MV:
        """
        Copies the monetary value with the given currency.
        """
        raise NotImplementedError

    def with_qty(self: MV, qty: Decimal) -> MV:
        """
        Copies the monetary value with the given quantity.
        """
        raise NotImplementedError

    def with_dov(self: MV, dov: Date) -> MV:
        """
        Copies the monetary value with the given date.
        """
        raise NotImplementedError

    def convert(self: MV, ccy: Currency, asof: Optional[Date] = None, strict: bool = False) -> MV:
        """
        Converts the monetary value from one currency to another.

        Raises :class:`FXRateLookupError` if no foreign exchange rate can be found for conversion.

        Note that we will carry the date forward as per ``asof`` date.
        """
        raise NotImplementedError

    @classmethod
    def of(cls, ccy: Optional[Currency], qty: Optional[Decimal], dov: Optional[Date]) -> MV:
        """
        Provides a factory method to create an instance of concrete monetary value object model in a safe manner.
        """
        raise NotImplementedError


class DefinedMonetaryValue(Generic[MV], MonetaryValue, namedtuple("DMV", ["ccy", "qty", "dov"])):  # type: ignore
    """
    Provides a partial implementation of *defined* monetary value model.
    """

    ## No need for slots.
    __slots__ = ()

    #: Indicates that instances of this class are *defined* monetary values.
    defined: bool = True  # noqa: E704

    #: Indicates that instances of this class are not *undefined* monetary values.
    undefined: bool = False

    def __bool__(self: MV) -> bool:
        return self.qty != 0

    def __float__(self: MV) -> float:
        return float(self.qty)

    def __int__(self: MV) -> int:
        return int(self.qty)

    def __lt__(self: MV, other: MV) -> bool:  # type: ignore
        if other.undefined:
            return False
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(self.ccy, other.ccy, "`<` comparison")
        return self.qty < other.qty

    def __le__(self: MV, other: MV) -> bool:  # type: ignore
        if other.undefined:
            return False
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(self.ccy, other.ccy, "`<=` comparison")
        return self.qty <= other.qty

    def __gt__(self: MV, other: MV) -> bool:  # type: ignore
        if other.undefined:
            return True
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(self.ccy, other.ccy, "`>` comparison")
        return self.qty > other.qty

    def __ge__(self: MV, other: MV) -> bool:  # type: ignore
        if other.undefined:
            return True
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(self.ccy, other.ccy, "`>=` comparison")
        return self.qty >= other.qty


class UndefinedMonetaryValue(Generic[MV], MonetaryValue):
    """
    Provides a partial implementation of *defined* monetary value model.
    """

    ## No need for slots.
    __slots__ = ()

    #: Indicates that instances of this class are not *defined* monetary values.
    defined: bool = False  # noqa: E704

    #: Indicates that instances of this class are *undefined* monetary values.
    undefined: bool = True

    @property
    def ccy(self) -> Currency:  # type: ignore
        raise TypeError("Undefined monetary value object does not have currency information.")

    @property
    def qty(self) -> Decimal:  # type: ignore
        raise TypeError("Undefined monetary value object does not have quantity information.")

    @property
    def dov(self) -> Date:  # type: ignore
        raise TypeError("Undefined monetary value object does not have value date information.")

    def __bool__(self: MV) -> bool:
        return False

    def __abs__(self: MV) -> MV:
        return self

    def __float__(self: MV) -> float:
        raise MonetaryOperationException("Can not call __float__ on an undefined monetary value.")

    def __int__(self: MV) -> int:
        raise MonetaryOperationException("Can not call __int__ on an undefined monetary value.")

    def __round__(self: MV, ndigits: int = 0) -> MV:
        return self

    def __neg__(self: MV) -> MV:
        return self

    def __pos__(self: MV) -> MV:
        return self

    def __mul__(self: MV, other: Union[Decimal, int, float]) -> MV:
        return self

    def __truediv__(self: MV, other: Union[Decimal, int, float]) -> MV:
        return self

    def __floordiv__(self: MV, other: Union[Decimal, int, float]) -> MV:
        return self

    def __lt__(self: MV, other: MV) -> bool:
        return other.defined

    def __le__(self: MV, other: MV) -> bool:
        return True

    def __gt__(self: MV, other: MV) -> bool:
        return False

    def __ge__(self: MV, other: MV) -> bool:
        return other.undefined

    def with_ccy(self: MV, ccy: Currency) -> MV:
        return self

    def with_qty(self: MV, qty: Decimal) -> MV:
        return self

    def with_dov(self: MV, dov: Date) -> MV:
        return self

    def convert(self: MV, ccy: Currency, asof: Optional[Date] = None, strict: bool = False) -> MV:
        return self


class Money(MonetaryValue["Money"]):
    """
    Defines a monetary value model with fixed precision as per the value currency.
    """

    ## No need for slots.
    __slots__ = ()

    @property
    def bigmoney(self) -> "BigMoney":
        """
        Returns the :class:`BigMoney` representation of the :class:`Money` instance.
        """
        raise NotImplementedError

    @classmethod
    def of(cls, ccy: Optional[Currency], qty: Optional[Decimal], dov: Optional[Date]) -> "Money":
        """
        Creates a new money instance in a safe manner.
        """
        if ccy is None or qty is None or dov is None:
            return NoMoney
        return SomeMoney(ccy, ccy.quantize(qty), dov)


class SomeMoney(Money, DefinedMonetaryValue["SomeMoney"]):  # type: ignore
    """
    Provides the *defined* :class:`Money` implementation.
    """

    ## No need for slots.
    __slots__ = ()

    @property
    def bigmoney(self) -> "BigMoney":
        return SomeBigMoney(*tuple(self))

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, SomeMoney) and tuple(self) == tuple(other)

    def __abs__(self) -> "SomeMoney":
        return SomeMoney(self[0], abs(self[1]), self[2])

    def __round__(self, ndigits: int = 0) -> "SomeMoney":
        return SomeMoney(self[0], round(self[1], ndigits), self[2])

    def __neg__(self) -> "SomeMoney":
        return SomeMoney(self[0], -self[1], self[2])

    def __pos__(self) -> "SomeMoney":
        return self

    def __mul__(self, other: Union[Decimal, int, float]) -> "SomeMoney":
        ccy = self[0]
        return SomeMoney(ccy, ccy.quantize(self[1] * other), self[2])

    def __truediv__(self, other: Union[Decimal, int, float]) -> "SomeMoney":
        ccy = self[0]
        return SomeMoney(ccy, ccy.quantize(self[1] / other), self[2])

    def __floordiv__(self, other: Union[Decimal, int, float]) -> "SomeMoney":
        ccy = self[0]
        return SomeMoney(ccy, ccy.quantize(self[1] // other), self[2])

    def __add__(self, other: Union[Money, Decimal, int, float]) -> "SomeMoney":
        if other.__class__ == SomeMoney:
            ## Get slots:
            ccy1, qty1, dov1 = self
            ccy2, qty2, dov2 = other  # type: ignore

            ## Check currencies:
            if ccy1 != ccy2:
                raise IncompatibleCurrencyError(ccy1, ccy2, "addition")
            else:
                return SomeMoney(ccy1, qty1 + qty2, max(dov1, dov2))
        elif other.__class__ == NoneMoney:
            return self
        else:
            ccy, qty, dov = self
            return SomeMoney(ccy, ccy.quantize(qty + other), dov)

    def __sub__(self, other: Union[Money, Decimal, int, float]) -> "SomeMoney":
        if other.__class__ == SomeMoney:
            ## Get slots:
            ccy1, qty1, dov1 = self
            ccy2, qty2, dov2 = other  # type: ignore

            ## Check currencies:
            if ccy1 != ccy2:
                raise IncompatibleCurrencyError(ccy1, ccy2, "addition")
            else:
                return SomeMoney(ccy1, qty1 - qty2, max(dov1, dov2))
        elif other.__class__ == NoneMoney:
            return self
        else:
            ccy, qty, dov = self
            return SomeMoney(ccy, ccy.quantize(qty - other), dov)

    def with_ccy(self, ccy: Currency) -> "SomeMoney":
        return SomeMoney(ccy, ccy.quantize(self[1]), self[2])

    def with_qty(self, qty: Decimal) -> "SomeMoney":
        ccy = self[0]
        return SomeMoney(ccy, ccy.quantize(qty), self[2])

    def with_dov(self, dov: Date) -> "SomeMoney":
        return SomeMoney(self[0], self[1], dov)

    def convert(self, ccy: Currency, asof: Optional[Date] = None, strict: bool = False) -> Money:
        ## Get our slots
        sccy, sqty, sdov = tuple(self)

        ## Get date of conversion:
        asof = asof or sdov

        ## Attempt to get the FX rate:
        try:
            rate = FXRateService.default.query(sccy, ccy, asof, strict)  # type: ignore
        except AttributeError as exc:
            if FXRateService.default is None:
                raise ProgrammingError("Did you implement and set the default FX rate service?")
            else:
                raise exc

        ## Do we have a rate?
        if rate is None:
            ## Nope, shall we raise exception?
            if strict:
                ## Yep:
                raise FXRateLookupError(sccy, ccy, asof)
            else:
                ## Just return NA:
                return NoMoney

        ## Compute and return:
        return SomeMoney(ccy, ccy.quantize(sqty * rate.value), asof)


class NoneMoney(Money, UndefinedMonetaryValue["SomeMoney"]):
    """
    Provides the *undefined* :class:`Money` implementation.
    """

    ## No need for slots.
    __slots__ = ()

    @property
    def bigmoney(self) -> "BigMoney":
        return NoBigMoney

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, NoneMoney)

    def __add__(self, other: Union[Money, Decimal, int, float]) -> Money:
        if isinstance(other, Money):
            return other
        return self

    def __sub__(self, other: Union[Money, Decimal, int, float]) -> Money:
        if isinstance(other, Money):
            return other
        return self


class BigMoney(MonetaryValue["BigMoney"]):
    """
    Defines a monetary value model with arbitrary precision.
    """

    ## No need for slots.
    __slots__ = ()

    @property
    def money(self) -> "Money":
        """
        Returns the :class:`Money` representation of the :class:`BigMoney` instance.
        """
        raise NotImplementedError

    @classmethod
    def of(cls, ccy: Optional[Currency], qty: Optional[Decimal], dov: Optional[Date]) -> "BigMoney":
        """
        Creates a new money instance in a safe manner.
        """
        if ccy is None or qty is None or dov is None:
            return NoBigMoney
        return SomeBigMoney(ccy, qty, dov)


class SomeBigMoney(BigMoney, DefinedMonetaryValue["SomeBigMoney"]):  # type: ignore
    """
    Provides the *defined* :class:`BigMoney` implementation.
    """

    ## No need for slots.
    __slots__ = ()

    @property
    def money(self) -> "Money":
        ccy = self[0]
        return SomeMoney(ccy, ccy.quantize(self[1]), self[2])

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, SomeBigMoney) and tuple(self) == tuple(other)

    def __abs__(self) -> "SomeBigMoney":
        return SomeBigMoney(self[0], abs(self[1]), self[2])

    def __round__(self, ndigits: int = 0) -> "SomeBigMoney":
        return SomeBigMoney(self[0], round(self[1], ndigits), self[2])

    def __neg__(self) -> "SomeBigMoney":
        return SomeBigMoney(self[0], -self[1], self[2])

    def __pos__(self) -> "SomeBigMoney":
        return self

    def __mul__(self, other: Union[Decimal, int, float]) -> "SomeBigMoney":
        return SomeBigMoney(self[0], self[1] * other, self[2])

    def __truediv__(self, other: Union[Decimal, int, float]) -> "SomeBigMoney":
        return SomeBigMoney(self[0], self[1] / other, self[2])

    def __floordiv__(self, other: Union[Decimal, int, float]) -> "SomeBigMoney":
        return SomeBigMoney(self[0], self[1] // other, self[2])

    def __add__(self, other: Union[BigMoney, Decimal, int, float]) -> "SomeBigMoney":
        if other.__class__ == SomeBigMoney:
            ## Get slots:
            ccy1, qty1, dov1 = self
            ccy2, qty2, dov2 = other  # type: ignore

            ## Check currencies:
            if ccy1 != ccy2:
                raise IncompatibleCurrencyError(ccy1, ccy2, "addition")
            else:
                return SomeBigMoney(ccy1, qty1 + qty2, max(dov1, dov2))
        elif other.__class__ == NoneBigMoney:
            return self
        else:
            ccy, qty, dov = self
            return SomeBigMoney(ccy, qty + other, dov)

    def __sub__(self, other: Union[BigMoney, Decimal, int, float]) -> "SomeBigMoney":
        if other.__class__ == SomeBigMoney:
            ## Get slots:
            ccy1, qty1, dov1 = self
            ccy2, qty2, dov2 = other  # type: ignore

            ## Check currencies:
            if ccy1 != ccy2:
                raise IncompatibleCurrencyError(ccy1, ccy2, "addition")
            else:
                return SomeBigMoney(ccy1, qty1 - qty2, max(dov1, dov2))
        elif other.__class__ == NoneBigMoney:
            return self
        else:
            ccy, qty, dov = self
            return SomeBigMoney(ccy, qty - other, dov)

    def with_ccy(self, ccy: Currency) -> "SomeBigMoney":
        return SomeBigMoney(ccy, self[1], self[2])

    def with_qty(self, qty: Decimal) -> "SomeBigMoney":
        return SomeBigMoney(self[0], qty, self[2])

    def with_dov(self, dov: Date) -> "SomeBigMoney":
        return SomeBigMoney(self[0], self[1], dov)

    def convert(self, ccy: Currency, asof: Optional[Date] = None, strict: bool = False) -> BigMoney:
        ## Get our slots
        sccy, sqty, sdov = tuple(self)

        ## Get date of conversion:
        asof = asof or sdov

        ## Attempt to get the FX rate:
        try:
            rate = FXRateService.default.query(sccy, ccy, asof, strict)  # type: ignore
        except AttributeError as exc:
            if FXRateService.default is None:
                raise ProgrammingError("Did you implement and set the default FX rate service?")
            else:
                raise exc

        ## Do we have a rate?
        if rate is None:
            ## Nope, shall we raise exception?
            if strict:
                ## Yep:
                raise FXRateLookupError(sccy, ccy, asof)
            else:
                ## Just return NA:
                return NoBigMoney

        ## Compute and return:
        return SomeBigMoney(ccy, sqty * rate.value, asof)


class NoneBigMoney(BigMoney, UndefinedMonetaryValue["NoneBigMoney"]):
    """
    Provides the *undefined* :class:`BigMoney` implementation.
    """

    ## No need for slots.
    __slots__ = ()

    @property
    def money(self) -> "Money":
        return NoMoney

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, NoneBigMoney)

    def __add__(self, other: Union[BigMoney, Decimal, int, float]) -> BigMoney:
        if isinstance(other, BigMoney):
            return other
        return self

    def __sub__(self, other: Union[BigMoney, Decimal, int, float]) -> BigMoney:
        if isinstance(other, BigMoney):
            return other
        return self


#: Defines a singleton NoneMoney:
NoMoney = NoneMoney()


#: Defines a singleton NoneBigMoney:
NoBigMoney = NoneBigMoney()


class IncompatibleCurrencyError(ValueError):
    """
    Provides an exception indicating that there is an attempt for performing monetary operations
    with incompatible currencies.
    """

    def __init__(self, ccy1: Currency, ccy2: Currency, operation: str="<Unspecified>") -> None:
        """
        Initializes an incompatible currency error message.
        """
        ## Keep sloys:
        self.ccy1 = ccy1
        self.ccy2 = ccy2
        self.operation = operation

        ## Call super:
        super().__init__(f"{ccy1.code} vs {ccy2.code} are incompatible for operation '{operation}'.")


class MonetaryOperationException(TypeError):
    """
    Provides an exception that a certain monetary operation can not be carried on.
    """
    pass
