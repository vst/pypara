import datetime
from decimal import Decimal
from typing import TypeVar, Generic, Callable, Optional, Any, Tuple, Union, SupportsRound, cast, SupportsAbs, Dict

import operator
from abc import abstractmethod, ABCMeta

from .currencies import Currency
from .exchange import FXRateService, FXRateLookupError
from .generic import MaxPrecisionQuantizer, Temporal, make_quantizer, ProgrammingError


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
        super().__init__(f"{ccy1} vs {ccy2} are incompatible for operation '{operation}'.")


#: Defines the self type (sic.) for the monetary value implementations.
MV = TypeVar("MV", bound="MonetaryValue", covariant=True)

#: Defines the 3-Tuple for monetary value object contents.
MVO = Tuple[Currency, Decimal, Temporal]

#: Defines a type alias for acceptable numeric values.
_Numeric = Union["MonetaryValue", Decimal, int, float]


class MonetaryValue(Generic[MV], SupportsRound[MV], SupportsAbs[MV], metaclass=ABCMeta):
    """
    Provides an abstract monetary value object model.
    """

    #: Limits slots.
    __slots__ = ()

    @property
    @abstractmethod
    def ccy(self) -> Currency:
        """
        Returns the currency of the monetary value.
        """
        pass

    @property
    @abstractmethod
    def qty(self) -> Decimal:
        """
        Returns the quantity of the monetary value.
        """
        pass

    @property
    @abstractmethod
    def dov(self) -> Temporal:
        """
        Returns the date of value of the monetary value.
        """
        pass

    @property
    @abstractmethod
    def defined(self) -> bool:
        """
        Indicates if the monetary value object is a defined value.
        """
        pass

    def __bool__(self) -> bool:
        """
        Provides the logical representation of the monetary value object.

        Note that a monetary value which is defined but yet has a ``qty`` of ``0`` is still logically ``True``
        as per our monetary semantics.
        """
        return self.defined

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """
        Checks the equality of two monetary value instances.
        """
        pass

    @abstractmethod
    def apply(self: MV, func: Callable[[Currency, Decimal, Temporal], Tuple[Currency, Decimal, Temporal]]) -> MV:
        """
        Provides a method to apply a function to the deconstructed monetary value object.
        """
        pass

    def arithmetic(self: MV, other: _Numeric, func: Callable[[Decimal, Decimal], Decimal]) -> MV:
        """
        Provides an addition operation.
        """
        ## Is the other a Decimal?
        if isinstance(other, Decimal) or isinstance(other, int) or isinstance(other, float):
            return self.apply(lambda x, y, z: (x, func(y, Decimal(cast(Union[Decimal, int, float], other))), z))

        ## Short circuits:
        if not other.defined:
            return self
        elif not self.defined:
            return self.of(other.ccy, other.qty, other.dov)
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(self.ccy, other.ccy, "binary arithmetic")

        ## By now, we expect that the two instances are defined monetary value objects. However, they may be of
        ## different type. Therefore, the second operand must be cast to the first operand type, if required:
        if type(self) is type(other):
            ## Yep, we have same types:
            coperand = cast(MV, other)
        else:
            ## Nope, they are not of same type. Cast the second operand:
            coperand = self.of(other.ccy, other.qty, other.dov)

        ## Now, perform the operation and return:
        return self.apply(lambda x, y, z: (x, func(y, coperand.qty), max(z, coperand.dov)))

    ## region Unary Operations
    def __neg__(self) -> MV:
        return self.apply(lambda x, y, z: (x, -y, z))

    def __pos__(self) -> MV:
        return self.apply(lambda x, y, z: (x, +y, z))

    def __abs__(self) -> MV:
        return self.apply(lambda x, y, z: (x, abs(y), z))

    def __float__(self) -> float:
        return float(self.qty) if self.defined else float("nan")
    ## endregion

    ## region Binary Operations
    def __round__(self, ndigits: int = 0) -> MV:
        return self.apply(lambda x, y, z: (x, y.quantize(make_quantizer(ndigits)), z))

    def __mul__(self, other: Union[Decimal, int, float]) -> MV:
        return self.apply(lambda x, y, z: (x, y * Decimal(other), z))

    def __truediv__(self, other: Union[Decimal, int, float]) -> MV:
        return self.apply(lambda x, y, z: (x, y / Decimal(other), z))

    def __floordiv__(self, other: Union[Decimal, int, float]) -> MV:
        return self.apply(lambda x, y, z: (x, y // Decimal(other), z))

    def __add__(self, other: Union["MonetaryValue", Decimal, int, float]) -> MV:
        """
        Provides the addition operation.
        """
        return self.arithmetic(other, operator.add)

    def __sub__(self, other: Union["MonetaryValue", Decimal, int, float]) -> MV:
        """
        Provides the subtraction operation.
        """
        return self.arithmetic(other, operator.sub)

    def __lt__(self, other: "MonetaryValue") -> bool:
        if not self.defined:
            return other.defined
        elif not other.defined:
            return False
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(self.ccy, other.ccy, "logical comparison")
        return self.qty < other.qty

    def __le__(self, other: "MonetaryValue") -> bool:
        if not self.defined:
            return True
        elif not other.defined:
            return False
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(self.ccy, other.ccy, "logical comparison")
        return self.qty <= other.qty

    def __gt__(self, other: "MonetaryValue") -> bool:
        if not self.defined:
            return False
        elif not other.defined:
            return True
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(self.ccy, other.ccy, "logical comparison")
        return self.qty > other.qty

    def __ge__(self, other: "MonetaryValue") -> bool:
        if not self.defined:
            return not other.defined
        elif not other.defined:
            return True
        elif self.ccy != other.ccy:
            raise IncompatibleCurrencyError(self.ccy, other.ccy, "logical comparison")
        return self.qty >= other.qty
    ## endregion

    def map_ccy(self: MV, func: Callable[[Currency], Currency]) -> MV:
        """
        Maps the currency of the monetary value object.
        """
        return self.apply(lambda x, y, z: (func(x), y, z))

    def map_qty(self: MV, func: Callable[[Decimal], Decimal]) -> MV:
        """
        Maps the quantity of the monetary value object.
        """
        return self.apply(lambda x, y, z: (x, func(y), z))

    def map_dov(self: MV, func: Callable[[Temporal], Temporal]) -> MV:
        """
        Maps the date of value of the monetary value object.
        """
        return self.apply(lambda x, y, z: (x, y, func(z)))

    def with_ccy(self: MV, ccy: Currency) -> MV:
        """
        Returns the monetary value with the given currency.
        """
        return self.apply(lambda x, y, z: (ccy, y, z))

    def with_qty(self: MV, qty: Decimal) -> MV:
        """
        Returns the monetary value with the given quantity.
        """
        return self.apply(lambda x, y, z: (x, qty, z))

    def with_dov(self: MV, dov: Temporal) -> MV:
        """
        Returns the monetary value with the given temporal dimension value.
        """
        return self.apply(lambda x, y, z: (x, y, dov))

    def convert(self: MV, ccy: Currency, asof: Optional[Temporal] = None, strict: bool = False) -> MV:
        """
        Converts the monetary amount.

        Note that the method raises exceptions if ``strict == True``.
        """
        ## Are we defined here?
        if not self.defined:
            return self

        ## Get date of conversion:
        asof = asof or self.dov

        ## Attempt to get the FX rate:
        if FXRateService.default is not None:
            rate = FXRateService.default.query(self.ccy, ccy, asof, strict)
        else:
            raise ProgrammingError("Did you implement and set the default FX rate service?")

        ## Do we have a rate?
        if rate is None:
            ## Nope, shall we raise exception?
            if strict:
                ## Yep:
                raise FXRateLookupError(self.ccy, ccy, asof)
            else:
                ## Just return NA:
                return self.of(None, None, None)

        ## Compute and return:
        return self.of(ccy, self.qty * rate.value, asof)

    @property
    def bigmoney(self) -> "BigMoney":
        """
        Returns the BigMoney representation of this.
        """
        if self.defined:
            return BigMoney.of(self.ccy, self.qty, self.dov)
        return NoBigMoney

    @property
    def money(self) -> "Money":
        """
        Returns the Money representation of this.
        """
        if self.defined:
            return Money.of(self.ccy, self.qty, self.dov)
        return NoMoney

    @property
    def primitive(self) -> Optional[Dict[str, Union[str, Decimal, Temporal]]]:
        """
        Returns a primitive representation of the monetary instance.
        """
        ## If undefined, simply return None:
        if not self.defined:
            return None

        ## Pack the data into dictionary and return:
        return {"ccy": self.ccy.code, "qty": self.qty, "dov": self.dov}

    @classmethod
    def of(cls, ccy: Optional[Currency], qty: Optional[Decimal], dov: Optional[datetime.date]) -> MV:
        """
        Provides a factory method to create an instance of concrete monetary value object model.
        """
        raise NotImplementedError


class DefinedMonetaryValue(MonetaryValue, Generic[MV], metaclass=ABCMeta):
    """
    Provides a defined monetary value object model mixin.
    """

    #: Limits slots.
    __slots__ = ()

    @property
    def defined(self) -> bool:
        """
        Indicates that the instance is an undefined monetary value object.
        """
        return True

    def __eq__(self, other: Any) -> bool:
        return type(self) is type(other) and self.ccy == other.ccy and self.qty == other.qty and self.dov == other.dov

    def __repr__(self) -> str:
        """
        Provides an internal string representation.
        """
        return f"<{self.__class__.__name__} {self.ccy} {self.qty} {self.dov}>"

    def apply(self: MV, func: Callable[[Currency, Decimal, Temporal], Tuple[Currency, Decimal, Temporal]]) -> MV:
        """
        Provides a method to apply a function to the deconstructed monetary value object.
        """
        return self.of(*func(self.ccy, self.qty, self.dov))


class UndefinedMonetaryValue(MonetaryValue, Generic[MV], metaclass=ABCMeta):
    """
    Provides an undefined monetary value object model mixin.
    """

    #: Limits slots.
    __slots__ = ()

    @property
    def ccy(self) -> Currency:
        raise TypeError("Undefined monetary value object does not have currency information.")

    @property
    def qty(self) -> Decimal:
        raise TypeError("Undefined monetary value object does not have quantity information.")

    @property
    def dov(self) -> datetime.date:
        raise TypeError("Undefined monetary value object does not have value date information.")

    @property
    def defined(self) -> bool:
        """
        Indicates that the instance is an undefined monetary value object.
        """
        return False

    def __eq__(self, other: Any) -> bool:
        return type(self) is type(other) and not self.defined and not other.defined

    def __repr__(self) -> str:
        """
        Provides an internal string representation.
        """
        return f"<{self.__class__.__name__}>"

    def apply(self: MV, func: Callable[[Currency, Decimal, Temporal], Tuple[Currency, Decimal, Temporal]]) -> MV:
        """
        Provides a method to apply a function to the deconstructed monetary value object.
        """
        return self


class BigMoney(MonetaryValue["BigMoney"], metaclass=ABCMeta):
    """
    Provides an (almost) arbitrary precision implementation of monetary value object model.
    """

    #: Limits slots.
    __slots__ = ()

    @classmethod
    def of(cls, ccy: Optional[Currency], qty: Optional[Decimal], dov: Optional[datetime.date]) -> "BigMoney":
        """
        Provides a factory method to create an instance of concrete monetary value object model.
        """
        if ccy is None or qty is None or dov is None:
            return NoneBigMoney()
        return SomeBigMoney(ccy, qty.quantize(MaxPrecisionQuantizer), dov)


class SomeBigMoney(DefinedMonetaryValue["SomeBigMoney"], BigMoney):
    """
    Provides a concrete, *defined* :class:`BigMoney` monetary value object model.
    """

    #: Defines the slots of the instance.
    __slots__ = ["__ccy", "__qty", "__dov"]

    def __init__(self, ccy: Currency, qty: Decimal, dov: datetime.date) -> None:
        """
        Initializes a :class:`BigMoney` instance.
        """
        self.__ccy = ccy
        self.__qty = qty
        self.__dov = dov

    @property
    def ccy(self) -> Currency:
        """
        Returns the currency of the montery value.
        """
        return self.__ccy

    @property
    def qty(self) -> Decimal:
        """
        Returns the quantity of the monetary value.
        """
        return self.__qty

    @property
    def dov(self) -> datetime.date:
        """
        Returns the date of value of the monetary value.
        """
        return self.__dov


class NoneBigMoney(UndefinedMonetaryValue["NoneBigMoney"], BigMoney):
    """
    Provides a :class:`BigMoney` implementation with undefined monetary value semantics.
    """

    #: Defines the singleton instance.
    __instance = None  # type: NoneBigMoney

    def __new__(cls,) -> "NoneBigMoney":
        """
        Creates the singleton instance, or returns the existing one.
        """
        ## Do we have the singleton instance?
        if NoneBigMoney.__instance is None:
            ## Nope, not yet. Creat one:
            NoneBigMoney.__instance = object.__new__(cls)

        ## Return the singleton instance.
        return NoneBigMoney.__instance


#: Defines a shorthand for undefined big money instances.
NoBigMoney: NoneBigMoney = NoneBigMoney()


class Money(MonetaryValue["Money"], metaclass=ABCMeta):
    """
    Provides an implementation of monetary value object model of which the precision is limited to the
    fractional units defined over the currency.
    """

    #: Limits slots.
    __slots__ = ()

    @classmethod
    def of(cls, ccy: Optional[Currency], qty: Optional[Decimal], dov: Optional[datetime.date]) -> "Money":
        """
        Provides a factory method to create an instance of concrete monetary value object model.
        """
        if ccy is None or qty is None or dov is None:
            return NoneMoney()
        return SomeMoney(ccy, ccy.quantize(qty), dov)


class SomeMoney(DefinedMonetaryValue["SomeMoney"], Money):
    """
    Provides a concrete, *defined* :class:`BigMoney` monetary value object model.
    """

    #: Defines the slots of the instance.
    __slots__ = ["__ccy", "__qty", "__dov"]

    def __init__(self, ccy: Currency, qty: Decimal, dov: datetime.date) -> None:
        """
        Initializes a :class:`Money` instance.
        """
        self.__ccy = ccy
        self.__qty = qty
        self.__dov = dov

    @property
    def ccy(self) -> Currency:
        """
        Returns the currency of the montery value.
        """
        return self.__ccy

    @property
    def qty(self) -> Decimal:
        """
        Returns the quantity of the monetary value.
        """
        return self.__qty

    @property
    def dov(self) -> datetime.date:
        """
        Returns the date of value of the monetary value.
        """
        return self.__dov


class NoneMoney(UndefinedMonetaryValue["NoneMoney"], Money):
    """
    Provides a :class:`Money` implementation with undefined monetary value semantics.
    """

    #: Defines the singleton instance.
    __instance = None  # type: NoneMoney

    def __new__(cls,) -> "NoneMoney":
        """
        Creates the singleton instance, or returns the existing one.
        """
        ## Do we have the singleton instance?
        if NoneMoney.__instance is None:
            ## Nope, not yet. Creat one:
            NoneMoney.__instance = object.__new__(cls)

        ## Return the singleton instance.
        return NoneMoney.__instance


#: Defines a shorthand for undefined money instances.
NoMoney: NoneMoney = NoneMoney()
