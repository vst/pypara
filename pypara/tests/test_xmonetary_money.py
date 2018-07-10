import datetime
from decimal import Decimal

import pytest

from pypara.currencies import Currencies
from pypara.xmonetary import Money, NoneMoney, SomeMoney, NoMoney, IncompatibleCurrencyError

## Define some currencies:
eur = Currencies["EUR"]
usd = Currencies["USD"]

## Defines some Decimal quantities:
zero = Decimal("0")
half = Decimal("0.5")
one = Decimal("1")
two = Decimal("2")

## Define some dates:
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)


def test_of():
    assert Money.of(usd, one, None) == Money.NA
    assert Money.of(usd, None, today) == Money.NA
    assert Money.of(usd, one, None) == Money.NA
    assert Money.of(usd, one, today) == SomeMoney(usd, one, today)


def test_is_equal():
    ## Vanilla:
    assert Money.NA.is_equal(NoMoney)
    assert Money.NA.is_equal(NoneMoney())
    assert not Money.NA.is_equal(Money.of(usd, zero, today))
    assert Money.of(usd, zero, today).is_equal(Money.of(usd, zero, today))
    assert Money.of(usd, half, today).is_equal(Money.of(usd, half, today))
    assert not Money.of(usd, zero, today).is_equal(Money.of(eur, zero, today))
    assert not Money.of(usd, zero, today).is_equal(Money.of(usd, half, today))
    assert not Money.of(usd, zero, today).is_equal(Money.of(usd, zero, yesterday))

    ## With operator overload:
    assert Money.NA == NoneMoney()
    assert Money.NA != Money.of(usd, zero, today)
    assert Money.of(usd, zero, today) == Money.of(usd, zero, today)
    assert Money.of(usd, half, today) == Money.of(usd, half, today)
    assert Money.of(usd, zero, today) != Money.of(eur, zero, today)
    assert Money.of(usd, zero, today) != Money.of(usd, half, today)
    assert Money.of(usd, zero, today) != Money.of(usd, zero, yesterday)


def test_to_boolean():
    ## Vanilla:
    assert not Money.NA.as_boolean()
    assert not Money.of(usd, zero, today).as_boolean()
    assert Money.of(usd, half, today).as_boolean()
    assert Money.of(usd, -half, today).as_boolean()

    ## With semantic overload
    assert not bool(Money.NA)
    assert not Money.of(usd, zero, today)
    assert Money.of(usd, half, today)
    assert Money.of(usd, -half, today)


def test_to_float():
    ## Vanilla:
    with pytest.raises(TypeError):
        Money.NA.as_float()
    assert Money.of(usd, half, today).as_float() == 0.5
    assert type(Money.of(usd, half, today).as_float()) == float

    ## With overload:
    with pytest.raises(TypeError):
        float(Money.NA)
    assert float(Money.of(usd, half, today)) == 0.5
    assert type(float(Money.of(usd, half, today))) == float


def test_to_integer():
    ## Vanilla:
    with pytest.raises(TypeError):
        int(Money.NA)
    assert int(Money.of(usd, half, today)) == 0
    assert type(int(Money.of(usd, half, today))) == int

    ## With overload:
    with pytest.raises(TypeError):
        Money.NA.as_integer()
    assert Money.of(usd, half, today).as_integer() == 0
    assert type(Money.of(usd, half, today).as_integer()) == int


def test_abs():
    ## Vanilla:
    assert Money.NA.abs() == Money.NA
    assert Money.of(usd, zero, today).abs() == Money.of(usd, zero, today)
    assert Money.of(usd, -one, today).abs() == Money.of(usd, +one, today)
    assert Money.of(usd, +one, today).abs() == Money.of(usd, +one, today)

    ## With overload:
    assert abs(Money.NA) == Money.NA
    assert abs(Money.of(usd, zero, today)) == Money.of(usd, zero, today)
    assert abs(Money.of(usd, -one, today)) == Money.of(usd, +one, today)
    assert abs(Money.of(usd, +one, today)) == Money.of(usd, +one, today)


def test_negative():
    ## Vanilla:
    assert Money.NA.negative() == Money.NA
    assert Money.of(usd, zero, today).negative() == Money.of(usd, zero, today)
    assert Money.of(usd, -one, today).negative() == Money.of(usd, +one, today)
    assert Money.of(usd, +one, today).negative() == Money.of(usd, -one, today)

    ## With overload:
    assert -Money.NA == Money.NA
    assert -Money.of(usd, zero, today) == Money.of(usd, zero, today)
    assert -Money.of(usd, -one, today) == Money.of(usd, +one, today)
    assert -Money.of(usd, +one, today) == Money.of(usd, -one, today)


def test_positive():
    ## Vanilla:
    assert Money.NA.positive() == Money.NA
    assert Money.of(usd, zero, today).positive() == Money.of(usd, zero, today)
    assert Money.of(usd, -one, today).positive() == Money.of(usd, -one, today)
    assert Money.of(usd, +one, today).positive() == Money.of(usd, +one, today)

    ## With overload:
    assert +Money.NA == Money.NA
    assert +Money.of(usd, zero, today) == Money.of(usd, zero, today)
    assert +Money.of(usd, -one, today) == Money.of(usd, -one, today)
    assert +Money.of(usd, +one, today) == Money.of(usd, +one, today)


def test_round():
    ## Vanilla:
    assert Money.NA.round(2) == Money.NA
    assert Money.of(usd, zero, today).round(2) == Money.of(usd, zero, today)
    assert Money.of(usd, -one, today).round(2) == Money.of(usd, -one, today)
    assert Money.of(usd, +one, today).round(2) == Money.of(usd, +one, today)

    ## Quick tests:
    assert Money.of(usd, Decimal("1.555"), today).round(2) == Money.of(usd, Decimal("1.56"), today)
    assert Money.of(usd, Decimal("1.545"), today).round(2) == Money.of(usd, Decimal("1.54"), today)

    ## With overload:
    assert round(Money.NA, 2) == Money.NA
    assert round(Money.of(usd, zero, today), 2) == Money.of(usd, zero, today)
    assert round(Money.of(usd, -one, today), 2) == Money.of(usd, -one, today)
    assert round(Money.of(usd, +one, today), 2) == Money.of(usd, +one, today)
    assert round(Money.of(usd, Decimal("1.555"), today), 2) == Money.of(usd, Decimal("1.56"), today)
    assert round(Money.of(usd, Decimal("1.545"), today), 2) == Money.of(usd, Decimal("1.54"), today)


def test_addition():
    ## First use `Money.NA`s:
    assert Money.NA.add(Money.NA) == Money.NA
    assert Money.NA.add(Money.of(usd, zero, today)) == Money.of(usd, zero, today)
    assert Money.of(usd, zero, today).add(Money.NA) == Money.of(usd, zero, today)

    ## Vanilla addition:
    assert Money.of(usd, zero, today).add(Money.of(usd, zero, today)) == Money.of(usd, zero, today)
    assert Money.of(usd, zero, today).add(Money.of(usd, one, today)) == Money.of(usd, one, today)
    assert Money.of(usd, one, today).add(Money.of(usd, one, today)) == Money.of(usd, two, today)
    assert Money.of(usd, one, today).add(Money.of(usd, -one, today)) == Money.of(usd, zero, today)

    ## Carry dates forward:
    assert Money.of(usd, zero, today).add(Money.of(usd, one, yesterday)) == Money.of(usd, one, today)
    assert Money.of(usd, zero, yesterday).add(Money.of(usd, one, today)) == Money.of(usd, one, today)

    ## Incompatible currency errors:
    with pytest.raises(IncompatibleCurrencyError):
        Money.of(usd, zero, today).add(Money.of(eur, zero, today))

    ## Operator overload:
    assert Money.NA + Money.NA == Money.NA
    assert Money.NA + Money.of(usd, zero, today) == Money.of(usd, zero, today)
    assert Money.of(usd, zero, today) + Money.NA == Money.of(usd, zero, today)
    assert Money.of(usd, zero, today) + Money.of(usd, one, today) == Money.of(usd, one, today)


def test_scalar_addition():
    ## First use `Money.NA`s:
    assert Money.NA.scalar_add(1) == Money.NA

    ## Vanilla addition:
    assert Money.of(usd, zero, today).scalar_add(1) == Money.of(usd, one, today)
    assert Money.of(usd, zero, today).scalar_add(1.0) == Money.of(usd, one, today)
    assert Money.of(usd, zero, today).scalar_add(one) == Money.of(usd, one, today)
    assert Money.of(usd, zero, today).scalar_add(-1) == Money.of(usd, -one, today)


def test_subtraction():
    ## First use `Money.NA`s:
    assert Money.NA.subtract(Money.NA) == Money.NA
    assert Money.NA.subtract(Money.of(usd, zero, today)) == Money.of(usd, zero, today)
    assert Money.of(usd, zero, today).subtract(Money.NA) == Money.of(usd, zero, today)

    ## Vanilla subtraction:
    assert Money.of(usd, zero, today).subtract(Money.of(usd, zero, today)) == Money.of(usd, zero, today)
    assert Money.of(usd, zero, today).subtract(Money.of(usd, one, today)) == Money.of(usd, -one, today)
    assert Money.of(usd, one, today).subtract(Money.of(usd, one, today)) == Money.of(usd, zero, today)
    assert Money.of(usd, one, today).subtract(Money.of(usd, -one, today)) == Money.of(usd, two, today)

    ## Carry dates forward:
    assert Money.of(usd, zero, today).subtract(Money.of(usd, one, yesterday)) == Money.of(usd, -one, today)
    assert Money.of(usd, zero, yesterday).subtract(Money.of(usd, one, today)) == Money.of(usd, -one, today)

    ## Incompatible currency errors:
    with pytest.raises(IncompatibleCurrencyError):
        Money.of(usd, zero, today).subtract(Money.of(eur, zero, today))

    ## Operator overload:
    assert Money.of(usd, zero, today) - Money.of(usd, one, today) == Money.of(usd, -one, today)
    assert Money.NA - Money.NA == Money.NA
    assert Money.NA - Money.of(usd, zero, today) == Money.of(usd, zero, today)
    assert Money.of(usd, zero, today) - Money.NA == Money.of(usd, zero, today)


def test_scalar_subtraction():
    ## First use `Money.NA`s:
    assert Money.NA.scalar_subtract(1) == Money.NA

    ## Vanilla subtraction:
    assert Money.of(usd, zero, today).scalar_subtract(1) == Money.of(usd, -one, today)
    assert Money.of(usd, zero, today).scalar_subtract(1.0) == Money.of(usd, -one, today)
    assert Money.of(usd, zero, today).scalar_subtract(one) == Money.of(usd, -one, today)
    assert Money.of(usd, zero, today).scalar_subtract(-1) == Money.of(usd, one, today)

    ## Operator overload:
    assert Money.of(usd, zero, today).scalar_subtract(1) == Money.of(usd, -one, today)
    assert Money.of(usd, zero, today).scalar_subtract(-1) == Money.of(usd, one, today)


def test_scalar_multiplication():
    ## First use `Money.NA`s:
    assert Money.NA.multiply(1) == Money.NA

    ## Vanilla subtraction:
    assert Money.of(usd, one, today).multiply(1) == Money.of(usd, one, today)
    assert Money.of(usd, one, today).multiply(2) == Money.of(usd, two, today)
    assert Money.of(usd, -one, today).multiply(1) == Money.of(usd, -one, today)
    assert Money.of(usd, -one, today).multiply(2) == Money.of(usd, -two, today)

    ## Other types:
    assert Money.of(usd, one, today).multiply(1) == Money.of(usd, one, today)
    assert Money.of(usd, one, today).multiply(1.0) == Money.of(usd, one, today)
    assert Money.of(usd, one, today).multiply(one) == Money.of(usd, one, today)

    ## Operator overload:
    assert Money.NA * 1 == Money.NA
    assert Money.of(usd, one, today) * 1 == Money.of(usd, one, today)
    assert Money.of(usd, one, today) * 2 == Money.of(usd, two, today)
    assert Money.of(usd, -one, today) * 1 == Money.of(usd, -one, today)
    assert Money.of(usd, -one, today) * 2 == Money.of(usd, -two, today)


def test_division():
    ## First use `Money.NA`s:
    assert Money.NA.divide(1) == Money.NA

    ## Vanilla subtraction:
    assert Money.of(usd, one, today).divide(1) == Money.of(usd, one, today)
    assert Money.of(usd, one, today).divide(2) == Money.of(usd, half, today)
    assert Money.of(usd, -one, today).divide(1) == Money.of(usd, -one, today)
    assert Money.of(usd, -one, today).divide(2) == Money.of(usd, -half, today)

    ## Various divisor types:
    assert Money.of(usd, one, today).divide(2) == Money.of(usd, half, today)
    assert Money.of(usd, one, today).divide(2.0) == Money.of(usd, half, today)
    assert Money.of(usd, one, today).divide(two) == Money.of(usd, half, today)

    ## Division by zero:
    assert Money.of(usd, one, today).divide(0) == Money.NA
    assert Money.of(usd, one, today).divide(zero) == Money.NA
    assert Money.of(usd, one, today).divide(0.0) == Money.NA

    ## Operator overload:
    assert Money.NA / 1 == Money.NA
    assert Money.of(usd, one, today) / 1 == Money.of(usd, one, today)
    assert Money.of(usd, one, today) / 2 == Money.of(usd, half, today)
    assert Money.of(usd, -one, today) / 1 == Money.of(usd, -one, today)
    assert Money.of(usd, -one, today) / 2 == Money.of(usd, -half, today)
    assert Money.of(usd, -one, today) / 0 == Money.NA


def test_floor_division():
    ## First use `Money.NA`s:
    assert Money.NA.floor_divide(1) == Money.NA

    ## Vanilla subtraction:
    assert Money.of(usd, one, today).floor_divide(1) == Money.of(usd, one, today)
    assert Money.of(usd, one, today).floor_divide(2) == Money.of(usd, zero, today)
    assert Money.of(usd, -one, today).floor_divide(1) == Money.of(usd, -one, today)
    assert Money.of(usd, -one, today).floor_divide(2) == Money.of(usd, zero, today)

    ## Various divisor types:
    assert Money.of(usd, one, today).floor_divide(2) == Money.of(usd, zero, today)
    assert Money.of(usd, one, today).floor_divide(2.0) == Money.of(usd, zero, today)
    assert Money.of(usd, one, today).floor_divide(two) == Money.of(usd, zero, today)

    ## Division by zero:
    assert Money.of(usd, one, today).floor_divide(0) == Money.NA
    assert Money.of(usd, one, today).floor_divide(zero) == Money.NA
    assert Money.of(usd, one, today).floor_divide(0.0) == Money.NA

    ## Operator overload:
    assert Money.NA / 1 == Money.NA
    assert Money.of(usd, one, today) // 1 == Money.of(usd, one, today)
    assert Money.of(usd, one, today) // 2 == Money.of(usd, zero, today)
    assert Money.of(usd, -one, today) // 1 == Money.of(usd, -one, today)
    assert Money.of(usd, -one, today) // 2 == Money.of(usd, zero, today)
    assert Money.of(usd, -one, today) // 0 == Money.NA


def test_comparisons():
    ## First use `Money.NA`s:
    assert not (Money.NA < Money.NA)
    assert Money.NA <= Money.NA
    assert not (Money.NA > Money.NA)
    assert Money.NA >= Money.NA

    ## Try mixed:
    assert Money.NA < Money.of(usd, -one, today)
    assert Money.NA <= Money.of(usd, -one, today)
    assert not (Money.NA > Money.of(usd, -one, today))
    assert not (Money.NA >= Money.of(usd, -one, today))

    ## ... and:
    assert not (Money.of(usd, -one, today) < Money.NA)
    assert not (Money.of(usd, -one, today) <= Money.NA)
    assert Money.of(usd, -one, today) > Money.NA
    assert Money.of(usd, -one, today) >= Money.NA

    ## With defined values:
    assert not (Money.of(usd, zero, today) < Money.of(usd, zero, today))
    assert Money.of(usd, zero, today) <= Money.of(usd, zero, today)
    assert not (Money.of(usd, zero, today) > Money.of(usd, zero, today))
    assert Money.of(usd, zero, today) >= Money.of(usd, zero, today)

    ## ... and:
    assert Money.of(usd, zero, today) < Money.of(usd, one, today)
    assert Money.of(usd, zero, today) <= Money.of(usd, one, today)
    assert not (Money.of(usd, zero, today) > Money.of(usd, one, today))
    assert not (Money.of(usd, zero, today) >= Money.of(usd, one, today))

    ## ... and:
    assert not (Money.of(usd, one, today) < Money.of(usd, zero, today))
    assert not (Money.of(usd, one, today) <= Money.of(usd, zero, today))
    assert Money.of(usd, one, today) > Money.of(usd, zero, today)
    assert Money.of(usd, one, today) >= Money.of(usd, zero, today)


def test_with():
    ## First use `Money.NA`s:
    assert Money.NA.with_ccy(usd) == Money.NA
    assert Money.NA.with_qty(one) == Money.NA
    assert Money.NA.with_dov(today) == Money.NA

    ## Now with some:
    assert Money.of(usd, zero, today).with_ccy(eur) == Money.of(eur, zero, today)
    assert Money.of(usd, zero, today).with_qty(one) == Money.of(usd, one, today)
    assert Money.of(usd, zero, today).with_dov(yesterday) == Money.of(usd, zero, yesterday)
