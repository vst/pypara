import datetime
from decimal import Decimal
from typing import Optional, Union


class ProgrammingError(Exception):
    """
    Provides a programming error exception.

    The rationale for this exception is to raise them whenever we rely on metaprogramming and
    the programmer has introduced a statement which breaks the coherence of the domain logic.
    """

    @classmethod
    def passert(cls, condition: bool, message: Optional[str]) -> None:
        """
        Raises a `ProgrammingError` if the condition is false.
        """
        if not condition:
            raise cls(message or "Broken coherence. Check your code against domain logic to fix it.")


def make_quantizer(precision: int) -> Decimal:
    """
    Creates a quantifier as per the given precision.
    """
    return Decimal(f"0.{''.join(['0' * precision])}")


#: Defines a type alias for acceptable numeric values.
Numeric = Union[Decimal, int, float]

#: Defines an alias for the temporal dimension of :mod:`pypara` implementation.
Date = datetime.date

#: Defines the maximum precision of the monetary values and operations.
MaxPrecision: int = 12

#: Defines the maximum precision quantifier.
MaxPrecisionQuantizer: Decimal = make_quantizer(MaxPrecision)

#: Defines the decimal constant for 0.
ZERO = Decimal("0")

#: Defines the decimal constant for 1.
ONE = Decimal("1")
