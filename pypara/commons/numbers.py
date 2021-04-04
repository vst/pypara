"""
This module provides common numeric type definitions, constants and functions.
"""

__all__ = [
    "Amount",
    "CENT",
    "DecimalLike",
    "HUNDRED",
    "MaxPrecision",
    "MaxPrecisionQuantizer",
    "Numeric",
    "ONE",
    "Quantity",
    "ZERO",
    "isum",
    "make_quantizer",
]

from decimal import Decimal
from typing import Iterable, NewType, Optional, TypeVar, cast

#: Defines a new-type for non-negative (absolute, unsigned) :py:class:`decimal.Decimal` values as *amount*.
#:
#: This is just a convenience for adding further semantics to type signatures.
Amount = NewType("Amount", Decimal)

#: Defines a new-type for :py:class:`decimal.Decimal` values as *quantities*.
#:
#: This is just a convenience for adding further semantics to type signatures.
Quantity = NewType("Quantity", Decimal)

#: Defines a type alias for numeric values.
Numeric = TypeVar("Numeric", int, float, Decimal, Amount, Quantity)

#: Defines a type variable for values of type either :py:class:`decimal.Decimal` or a sub-class or new-type based on
#: py:class:`Decimal` such as :py:class:`Amount` and a :py:class:`Quantity`.
DecimalLike = TypeVar("DecimalLike", bound=Decimal)

#: Defines the constant for :py:class:`decimal.Decimal` value ``0``.
ZERO = Decimal("0")

#: Defines the constant for :py:class:`decimal.Decimal` value ``0.01``.
CENT = Decimal("0.01")

#: Defines the constant for :py:class:`decimal.Decimal` value ``1``.
ONE = Decimal("1")

#: Defines the constant for :py:class:`decimal.Decimal` value ``100``.
HUNDRED = Decimal("100")


def make_quantizer(precision: int) -> Decimal:
    """
    Creates a quantifier as per the given precision.
    """
    return Decimal(f"0.{''.join(['0' * precision])}")


#: Defines the maximum precision of the monetary values and operations in this library.
MaxPrecision: int = 12

#: Defines the maximum precision quantifier.
MaxPrecisionQuantizer: Decimal = make_quantizer(MaxPrecision)


def isum(xs: Iterable[DecimalLike], start: Optional[DecimalLike] = None) -> DecimalLike:
    """
    Computes the sum of an iterable of :py:class:`DecimalLike` values such as :py:class:`Amount` or
    :py:class:`Quantity` including :py:class:`Decimal` itself.

    The return type is the same as the input element type. The base condition is :py:const:`ZERO` of
    :py:class:`decimal.Decimal` type but cast to the type variable if required.

    :param xs: An iterable of :py:class:`Decimal`-like values.
    :param start: Optional initial value. This defaults to :py:const:`ZERO` in the implementation.
    :return: Sum of the elements in the same type as the elements in the argument.

    >>> isum([Amount(ONE), Amount(ONE)])  # Return value is of type `Amount` during type-checking.
    Decimal('2')
    >>> isum([Quantity(ONE), Quantity(ONE)])  # Return value is of type `Quantity` during type-checking.
    Decimal('2')
    >>> isum([Amount(ONE), Amount(ONE)], Amount(ONE))  # Return value is of type `Amount` during type-checking.
    Decimal('3')
    >>> isum([Quantity(ONE), Quantity(ONE)], Quantity(ONE))  # Return value is of type `Quantity` during type-checking.
    Decimal('3')
    """
    return sum(xs, start or cast(DecimalLike, ZERO))
