import datetime
from decimal import Decimal


class ProgrammingError(Exception):
    """
    Provides a programming error exception.
    """
    pass


def make_quantizer(precision: int) -> Decimal:
    """
    Creates a quantifier as per the given precision.
    """
    return Decimal(f"0.{''.join(['0' * precision])}")


#: Defines an alias for the temporal dimension of monetary value implementations.
Temporal = datetime.date

#: Defines the maximum precision of the monetary values and operations.
MaxPrecision: int = 12

#: Defines the maximum precision quantifier.
MaxPrecisionQuantizer: Decimal = make_quantizer(MaxPrecision)
