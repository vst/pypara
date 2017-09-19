import datetime
from decimal import Decimal

from pypara.currencies import Currencies
from pypara.monetary import NoneMoney, NoneBigMoney, Money, BigMoney

## Define shorthands decimals:
ZERO = Decimal(0)
ONE = Decimal(1)
TEN = Decimal(10)
F_1_250 = Decimal("1.250")
F_1_265 = Decimal("1.265")
F_2_510 = Decimal("2.510")
F_2_515 = Decimal("2.515")

## Define shorthand currencies:
USD = Currencies["USD"]
EUR = Currencies["EUR"]

## Define shorthand dates:
today = datetime.date.today()
yesterday = today - datetime.timedelta(days=1)
tomorrow = today + datetime.timedelta(days=1)

## Define some monies:
M_USD_0_T0 = Money.of(USD, ZERO, today)
M_USD_0_T1 = Money.of(USD, ZERO, tomorrow)
M_EUR_0_T0 = Money.of(EUR, ZERO, today)
M_EUR_0_T1 = Money.of(EUR, ZERO, tomorrow)
M_USD_1_T0 = Money.of(USD, ONE, today)
M_USD_1_T1 = Money.of(USD, ONE, tomorrow)
M_EUR_1_T0 = Money.of(EUR, ONE, today)
M_EUR_1_T1 = Money.of(EUR, ONE, tomorrow)
M_USD_10_T0 = Money.of(USD, TEN, today)
M_USD_10_T1 = Money.of(USD, TEN, tomorrow)
M_EUR_10_T0 = Money.of(EUR, TEN, today)
M_EUR_10_T1 = Money.of(EUR, TEN, tomorrow)

B_USD_0_T0 = BigMoney.of(USD, ZERO, today)
B_USD_0_T1 = BigMoney.of(USD, ZERO, tomorrow)
B_EUR_0_T0 = BigMoney.of(EUR, ZERO, today)
B_EUR_0_T1 = BigMoney.of(EUR, ZERO, tomorrow)
B_USD_1_T0 = BigMoney.of(USD, ONE, today)
B_USD_1_T1 = BigMoney.of(USD, ONE, tomorrow)
B_EUR_1_T0 = BigMoney.of(EUR, ONE, today)
B_EUR_1_T1 = BigMoney.of(EUR, ONE, tomorrow)
B_USD_10_T0 = BigMoney.of(USD, TEN, today)
B_USD_10_T1 = BigMoney.of(USD, TEN, tomorrow)
B_EUR_10_T0 = BigMoney.of(EUR, TEN, today)
B_EUR_10_T1 = BigMoney.of(EUR, TEN, tomorrow)


def test_bool() -> None:
    """
    Tests the :method:`MonetaryValue.__bool__` method.
    """
    assert not NoneMoney()
    assert not NoneBigMoney()
    assert Money.of(USD, ZERO, today)
    assert Money.of(USD, ONE, today)
    assert BigMoney.of(USD, ZERO, today)
    assert BigMoney.of(USD, ONE, today)
    assert not Money.of(None, ZERO, today)
    assert not Money.of(USD, None, today)
    assert not Money.of(USD, ZERO, None)


def test_equality() -> None:
    """
    Tests the :method:`MonetaryValue.__eq__` method.
    """
    assert NoneMoney() == NoneMoney()
    assert NoneMoney() == Money.of(None, None, None)
    assert NoneBigMoney() == NoneBigMoney()
    assert NoneBigMoney() == BigMoney.of(None, None, None)
    assert NoneMoney() != NoneBigMoney()
    assert NoneMoney() != BigMoney.of(None, None, None)
    assert Money.of(USD, ZERO, today) == Money.of(USD, ZERO, today)
    assert BigMoney.of(USD, ZERO, today) == BigMoney.of(USD, ZERO, today)


def test_abs() -> None:
    """
    Tests the :method:`MonetaryValue.__abs__` method.
    """
    assert abs(NoneMoney()) == NoneMoney()


def test_apply_undefined() -> None:
    """
    Tests the :method:`UndefinedMonetaryValue.apply` method.
    """
    assert NoneMoney().apply(lambda x, y, z: (x, y, z)) == NoneMoney()
    assert NoneBigMoney().apply(lambda x, y, z: (x, y, z)) == NoneBigMoney()


def test_apply_defined_money() -> None:
    """
    Tests the :method:`SomeMoney.apply` method.
    """
    assert Money.of(USD, ZERO, today).apply(lambda x, y, z: (EUR, y, z)) == Money.of(EUR, ZERO, today)
    assert Money.of(USD, ZERO, today).apply(lambda x, y, z: (x, y + ONE, z)) == Money.of(USD, ONE, today)
    assert Money.of(USD, ZERO, today).apply(lambda x, y, z: (x, y, tomorrow)) == Money.of(USD, ZERO, tomorrow)
    assert Money.of(USD, ZERO, today).apply(lambda x, y, z: (EUR, y + ONE, tomorrow)) == Money.of(EUR, ONE, tomorrow)


def test_multiply() -> None:
    """
    Tests the :method:`MonetaryValue.__mul__` method.
    """
    assert NoneBigMoney() * 1000 == NoneBigMoney()
    assert B_USD_1_T0 * 1 == B_USD_1_T0
    assert B_USD_1_T0 * Decimal("1.5") == B_USD_1_T0.map_qty(lambda _: Decimal("1.5"))
    assert B_USD_1_T0 * Decimal("1.555") == B_USD_1_T0.map_qty(lambda _: Decimal("1.555"))
    assert B_USD_1_T0 * Decimal("1.565") == B_USD_1_T0.map_qty(lambda _: Decimal("1.565"))

    assert NoneMoney() * 1000 == NoneMoney()
    assert M_USD_1_T0 * 1 == M_USD_1_T0
    assert M_USD_1_T0 * Decimal("1.5") == M_USD_1_T0.map_qty(lambda _: Decimal("1.5"))
    assert M_USD_1_T0 * Decimal("1.555") == M_USD_1_T0.map_qty(lambda _: Decimal("1.56"))
    assert M_USD_1_T0 * Decimal("1.565") == M_USD_1_T0.map_qty(lambda _: Decimal("1.56"))


def test_truediv() -> None:
    """
    Tests the :method:`MonetaryValue.__truediv__` method.
    """
    assert NoneBigMoney() / 1000 == NoneBigMoney()
    assert B_USD_10_T0 / 1 == B_USD_10_T0
    assert B_USD_10_T0 / Decimal("2.00") == B_USD_10_T0.map_qty(lambda _: Decimal("5.00"))
    assert B_USD_10_T0 / Decimal("2.50") == B_USD_10_T0.map_qty(lambda _: Decimal("4.00"))
    assert B_USD_10_T0 / Decimal("3.00") == B_USD_10_T0.map_qty(lambda _: Decimal("3.333333333333"))

    assert NoneMoney() * 1000 == NoneMoney()
    assert M_USD_10_T0 / 1 == M_USD_10_T0
    assert M_USD_10_T0 / Decimal("2.00") == M_USD_10_T0.map_qty(lambda _: Decimal("5.00"))
    assert M_USD_10_T0 / Decimal("2.50") == M_USD_10_T0.map_qty(lambda _: Decimal("4.00"))
    assert M_USD_10_T0 / Decimal("3.00") == M_USD_10_T0.map_qty(lambda _: Decimal("3.33"))


def test_floordiv() -> None:
    """
    Tests the :method:`MonetaryValue.__floordiv__` method.
    """
    assert NoneBigMoney() // 1000 == NoneBigMoney()
    assert B_USD_10_T0 // 1 == B_USD_10_T0
    assert B_USD_10_T0 // Decimal("2.00") == B_USD_10_T0.map_qty(lambda _: Decimal("5"))
    assert B_USD_10_T0 // Decimal("2.50") == B_USD_10_T0.map_qty(lambda _: Decimal("4"))
    assert B_USD_10_T0 // Decimal("3.00") == B_USD_10_T0.map_qty(lambda _: Decimal("3"))

    assert NoneMoney() * 1000 == NoneMoney()
    assert M_USD_10_T0 // 1 == M_USD_10_T0
    assert M_USD_10_T0 // Decimal("2.00") == M_USD_10_T0.map_qty(lambda _: Decimal("5"))
    assert M_USD_10_T0 // Decimal("2.50") == M_USD_10_T0.map_qty(lambda _: Decimal("4"))
    assert M_USD_10_T0 // Decimal("3.00") == M_USD_10_T0.map_qty(lambda _: Decimal("3"))


def test_round() -> None:
    """
    Tests the :method:`MonetaryValue.__round__` method.
    """
    assert round(NoneBigMoney(), 0) == NoneBigMoney()
    assert round(NoneBigMoney(), 2) == NoneBigMoney()
    assert round(BigMoney.of(USD, Decimal("1.11115"), today), 4) == BigMoney.of(USD, Decimal("1.1112"), today)
    assert round(BigMoney.of(USD, Decimal("1.11125"), today), 4) == BigMoney.of(USD, Decimal("1.1112"), today)

    assert round(NoneMoney(), 0) == NoneMoney()
    assert round(NoneMoney(), 2) == NoneMoney()
    assert round(Money.of(USD, Decimal("1.11115"), today), 4) == Money.of(USD, Decimal("1.11"), today)
    assert round(Money.of(USD, Decimal("1.11125"), today), 4) == Money.of(USD, Decimal("1.11"), today)
    assert round(Money.of(USD, Decimal("1.1145"), today), 4) == Money.of(USD, Decimal("1.11"), today)
    assert round(Money.of(USD, Decimal("1.1245"), today), 4) == Money.of(USD, Decimal("1.12"), today)
    assert round(Money.of(USD, Decimal("1.115"), today), 4) == Money.of(USD, Decimal("1.12"), today)
    assert round(Money.of(USD, Decimal("1.125"), today), 4) == Money.of(USD, Decimal("1.12"), today)


def test_addition_nones() -> None:
    """
    Tests the :method:`MonetaryValue.__add__` method.
    """
    assert NoneBigMoney() + NoneBigMoney() == NoneBigMoney()
    assert NoneBigMoney() + B_USD_1_T0 == B_USD_1_T0
    assert NoneBigMoney() + M_USD_1_T0 == B_USD_1_T0
    assert NoneBigMoney() + NoneMoney() == NoneBigMoney()

    assert NoneMoney() + NoneMoney() == NoneMoney()
    assert NoneMoney() + M_USD_1_T0 == M_USD_1_T0
    assert NoneMoney() + B_USD_1_T0 == M_USD_1_T0
    assert NoneMoney() + NoneBigMoney() == NoneMoney()

    assert NoneBigMoney() + 10 == NoneBigMoney()
    assert NoneBigMoney() + 10.0 == NoneBigMoney()
    assert NoneBigMoney() + Decimal(10) == NoneBigMoney()
    assert NoneMoney() + 10 == NoneMoney()
    assert NoneMoney() + 10.0 == NoneMoney()
    assert NoneMoney() + Decimal(10) == NoneMoney()


def test_addition_somes_homogenous() -> None:
    """
    Tests the :method:`MonetaryValue.__add__` method.
    """
    assert B_USD_0_T0 + B_USD_1_T0 == B_USD_1_T0
    assert B_USD_1_T0 + B_USD_0_T0 == B_USD_1_T0
    assert B_USD_1_T0 + B_USD_10_T0 == BigMoney.of(USD, Decimal(11), today)
    assert B_USD_1_T0 + B_USD_10_T1 == BigMoney.of(USD, Decimal(11), tomorrow)
    assert B_USD_1_T1 + B_USD_10_T0 == BigMoney.of(USD, Decimal(11), tomorrow)

    assert M_USD_0_T0 + M_USD_1_T0 == M_USD_1_T0
    assert M_USD_1_T0 + M_USD_0_T0 == M_USD_1_T0
    assert M_USD_1_T0 + M_USD_10_T0 == Money.of(USD, Decimal(11), today)
    assert M_USD_1_T0 + M_USD_10_T1 == Money.of(USD, Decimal(11), tomorrow)
    assert M_USD_1_T1 + M_USD_10_T0 == Money.of(USD, Decimal(11), tomorrow)


def test_addition_somes_heterogenous() -> None:
    """
    Tests the :method:`MonetaryValue.__add__` method.
    """
    assert B_USD_0_T0 + M_USD_1_T0 == B_USD_1_T0
    assert B_USD_1_T0 + M_USD_0_T0 == B_USD_1_T0
    assert B_USD_1_T0 + M_USD_10_T0 == BigMoney.of(USD, Decimal(11), today)
    assert B_USD_1_T0 + M_USD_10_T1 == BigMoney.of(USD, Decimal(11), tomorrow)
    assert B_USD_1_T1 + M_USD_10_T0 == BigMoney.of(USD, Decimal(11), tomorrow)

    assert M_USD_0_T0 + B_USD_1_T0 == M_USD_1_T0
    assert M_USD_1_T0 + B_USD_0_T0 == M_USD_1_T0
    assert M_USD_1_T0 + B_USD_10_T0 == Money.of(USD, Decimal(11), today)
    assert M_USD_1_T0 + B_USD_10_T1 == Money.of(USD, Decimal(11), tomorrow)
    assert M_USD_1_T1 + B_USD_10_T0 == Money.of(USD, Decimal(11), tomorrow)

    assert Money.of(USD, F_1_250, today) + BigMoney.of(USD, F_1_265, tomorrow) == Money.of(USD, F_2_510, tomorrow)
    assert BigMoney.of(USD, F_1_265, tomorrow) + Money.of(USD, F_1_250, today) == BigMoney.of(USD, F_2_515, tomorrow)


def test_addition_somes_currency_exceptions() -> None:
    """
    Tests currency mismatch exceptions for addition.
    """
    ## TODO: Complete tests.
    pass


def test_comparison() -> None:
    """
    Tests comparison operators.
    """
    ## TODO: Complete tests.
    pass
