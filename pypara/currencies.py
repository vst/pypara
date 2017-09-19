from decimal import Decimal
from typing import Dict, List, Tuple, Optional, Type, Any, Callable  # noqa: F401

from collections import OrderedDict
from enum import Enum

from .generic import MaxPrecisionQuantizer, ProgrammingError, make_quantizer


class CurrencyLookupError(LookupError):
    """
    Provides a currency lookup error.
    """

    def __init__(self, code: str) -> None:
        """
        Initializes a currency lookup error.
        """
        ## Keep the code:
        self.code = code

        ## Set the message:
        super().__init__(f"Currency identified by code '{code}' does not exist")


class CurrencyType(Enum):
    """
    Defines available currency types.
    """

    #: Defines money currency as in common legal tender.
    MONEY = "Money"

    #: Defines precious metals currency type.
    METAL = "Precious Metal"

    #: Defines crypto currency type.
    CRYPTO = "Crypto Currency"

    #: Defines alternative currency type.
    ALTERNATIVE = "Alernative"


class Currency:
    """
    Defines currency value object model which is extending ISO 4217 to embrace other currency types.

    Note that you should not call :class:`Currency` constructor directly, but instead use the :method:`Currency.build`.
    :method:`Currency.build` is responsible of performing some checks before creating the currency.

    >>> Currency("XXX", "My Currency", 2)
    <Currency XXX>
    >>> USD = Currency("USD", "US Dollars", 2)
    >>> USD.quantize(Decimal("1.005"))
    Decimal('1.00')
    >>> USD.quantize(Decimal("1.015"))
    Decimal('1.02')
    >>> JPY = Currency("JPY", "Japanese Yen", 0)
    >>> JPY.quantize(Decimal("0.5"))
    Decimal('0')
    >>> JPY.quantize(Decimal("1.5"))
    Decimal('2')
    >>> ZZZ = Currency("ZZZ", "Some weird currency", -1)
    >>> ZZZ.quantize(Decimal("1.0000000000005"))
    Decimal('1.000000000000')
    >>> ZZZ.quantize(Decimal("1.0000000000015"))
    Decimal('1.000000000002')
    """

    #: Limit instance attributes.
    __slots__ = ["__code", "__name", "__decimals", "__quantizer", "__ctype"]

    def __init__(self, code: str, name: str, decimals: int, ctype: CurrencyType = CurrencyType.MONEY) -> None:
        """
        Creates a currency value object model instance.
        """
        ## Check the code:
        assert isinstance(code, str)
        assert len(code) == 3
        assert code.isalpha()
        assert code.isupper()
        assert " " not in code

        ## Check the name:
        assert isinstance(name, str)
        assert name
        assert not name.startswith(" ")
        assert not name.endswith(" ")

        ## Check the decimals:
        assert isinstance(decimals, int)
        assert decimals >= -1

        ## Check the ctype:
        assert isinstance(ctype, CurrencyType)

        ## Define the quantizer:
        if decimals < 0:
            quantizer = MaxPrecisionQuantizer
        elif decimals == 0:
            quantizer = Decimal("0")
        else:
            quantizer = make_quantizer(decimals)

        ## Setup slots:
        self.__code = code
        self.__name = name
        self.__decimals = decimals
        self.__quantizer = quantizer
        self.__ctype = ctype

    @property
    def code(self) -> str:
        """
        Returns the code of the currency.
        """
        return self.__code

    @property
    def name(self) -> str:
        """
        Returns the name of the currency.
        """
        return self.__name

    @property
    def decimals(self) -> int:
        """
        Returns the number of decimal points as per the fractional units of the currency.
        """
        return self.__decimals

    @property
    def type(self) -> CurrencyType:
        """
        Returns the type of the currency.
        """
        return self.__ctype

    def __repr__(self) -> str:
        """
        Provides an internal string representation of the :class:`Currency` instance.
        """
        return f"<Currency {self.__code}>"

    def quantize(self, qty: Decimal) -> Decimal:
        """
        Quantizes the decimal ``qty`` wrt to ccy's minor units fraction. Note that
        the [ROUND HALF TO EVEN](https://en.wikipedia.org/wiki/Rounding) method
        is used for rounding purposes.
        """
        return qty.quantize(self.__quantizer)


class CurrencyRegistry:
    """
    Defines a currency registry model.

    >>> "USD" in Currencies
    True
    >>> Currencies.has("USD")
    True
    >>> "XXX" in Currencies
    False
    >>> Currencies.has("XXX")
    False
    >>> Currencies["USD"]
    <Currency USD>
    >>> Currencies.get("USD")
    <Currency USD>
    >>> assert Currencies["USD"] == Currencies.get("USD")
    >>> Currencies.get("XXX")
    >>> Currencies.get("XXX", default=Currencies["USD"])
    <Currency USD>
    >>> assert len(Currencies) == len(Currencies.all)
    >>> assert Currencies.codes == [currency.code for currency in Currencies.all]
    >>> assert Currencies.codenames == [(currency.code, currency.name) for currency in Currencies.all]
    """

    #: Defines the singleton instance.
    __instance = None  # type: CurrencyRegistry

    def __new__(cls) -> "CurrencyRegistry":
        """
        Creates the singleton instance, or returns the existing one.
        """
        ## Do we have the singleton instance?
        if CurrencyRegistry.__instance is None:
            ## Nope, not yet. Creat one:
            CurrencyRegistry.__instance = object.__new__(cls)

        ## Return the singleton instance.
        return CurrencyRegistry.__instance

    def __init__(self) -> None:
        """
        Initializes the currency registry.
        """
        ## Initialize the master registry container.
        self.__registry: Dict[str, Currency] = OrderedDict([])

        ## Initialize the currencies buffer.
        self.__currencies: List[Currency] = []

        ## Initialize the currency codes buffer.
        self.__codes: List[str] = []

        ## Initialize the code/name tuples buffer.
        self.__codenames: List[Tuple[str, str]] = []

        ## Define the registry population context open/close flag.
        self.__ctx_open: bool = False

    def __enter__(self) -> Callable[[Currency], None]:
        """
        Enters the registry population context.
        """
        ## Mark the context as open:
        self.__ctx_open = True

        ## OK, return the add method:
        return self.__register

    def __exit__(self, exc_type: Optional[Type[Exception]], exc_value: Optional[str], tracebackx: Any) -> None:
        """
        Exits the registry population context and performs some finalization tasks.
        """
        ## Re-sort the registry:
        self.__registry = OrderedDict([(c.code, c) for c in sorted(self.__registry.values(), key=lambda x: x.code)])

        ## Re-sort currencies buffer:
        self.__currencies = [c for c in self.__registry.values()]

        ## Re-sort the currency codes buffer:
        self.__codes = [c.code for c in self.__currencies]

        ## Re-sort the choices buffer
        self.__codenames = [(c.code, c.name) for c in self.__currencies]

        ## Close the context:
        self.__ctx_open = False

    def __register(self, currency: Currency) -> None:
        """
        Attempts to add the currency to the registry.
        """
        ## Check of the registry population context is open:
        if not self.__ctx_open:
            ## Nope, raise error:
            raise ProgrammingError("Can not create currencies outside registry context.")

        ## Check if the currency is already added:
        if currency.code in self.__registry:
            raise ValueError(f"Currency {currency.code} is already registered.")

        ## Add to the containers:
        self.__registry[currency.code] = currency

    def __len__(self) -> int:
        """
        Returns the number of registered currencies.
        """
        return len(self.__registry)

    def __contains__(self, code: str) -> bool:
        """
        Checks if a given currency code is available.
        """
        return code in self.__registry

    def __getitem__(self, code: str) -> Currency:
        """
        Returns the currency identified by the code or raises lookup error.
        """
        try:
            return self.__registry[code]
        except KeyError:
            raise CurrencyLookupError(code)

    def has(self, code: str) -> bool:
        """
        Indicates if the code is a valid currency code.
        """
        return code in self.__registry

    def get(self, code: str, default: Optional[Currency]=None) -> Optional[Currency]:
        """
        Returns the currency for the given code.

        Note that if the code is not a valid currency code, a currency lookup error is raised.
        """
        try:
            return self.__registry[code]
        except KeyError:
            return default

    @property
    def all(self) -> List["Currency"]:
        """
        Returns the list of currencies.
        """
        return self.__currencies

    @property
    def codes(self) -> List[str]:
        """
        Returns a list of codes.
        """
        return self.__codes

    @property
    def codenames(self) -> List[Tuple[str, str]]:
        """
        Returns a list of code/name tuples.
        """
        return self.__codenames


#: Defines the global currencies registry.
Currencies = CurrencyRegistry()


## Create and register currencies in one go:
with Currencies as register:
    register(Currency("AED", "UAE Dirham", 2, CurrencyType.MONEY))
    register(Currency("AFN", "Afghani", 2, CurrencyType.MONEY))
    register(Currency("ALL", "Lek", 2, CurrencyType.MONEY))
    register(Currency("AMD", "Armenian Dram", 2, CurrencyType.MONEY))
    register(Currency("ANG", "Netherlands Antillean Guilder", 2, CurrencyType.MONEY))
    register(Currency("AOA", "Kwanza", 2, CurrencyType.MONEY))
    register(Currency("ARS", "Argentine Peso", 2, CurrencyType.MONEY))
    register(Currency("AUD", "Australian Dollar", 2, CurrencyType.MONEY))
    register(Currency("AWG", "Aruban Florin", 2, CurrencyType.MONEY))
    register(Currency("AZN", "Azerbaijanian Manat", 2, CurrencyType.MONEY))
    register(Currency("BAM", "Convertible Mark", 2, CurrencyType.MONEY))
    register(Currency("BBD", "Barbados Dollar", 2, CurrencyType.MONEY))
    register(Currency("BDT", "Taka", 2, CurrencyType.MONEY))
    register(Currency("BGN", "Bulgarian Lev", 2, CurrencyType.MONEY))
    register(Currency("BHD", "Bahraini Dinar", 3, CurrencyType.MONEY))
    register(Currency("BIF", "Burundi Franc", 0, CurrencyType.MONEY))
    register(Currency("BMD", "Bermudian Dollar", 2, CurrencyType.MONEY))
    register(Currency("BND", "Brunei Dollar", 2, CurrencyType.MONEY))
    register(Currency("BOB", "Boliviano", 2, CurrencyType.MONEY))
    register(Currency("BOV", "Mvdol", 2, CurrencyType.MONEY))
    register(Currency("BRL", "Brazilian Real", 2, CurrencyType.MONEY))
    register(Currency("BSD", "Bahamian Dollar", 2, CurrencyType.MONEY))
    register(Currency("BTN", "Ngultrum", 2, CurrencyType.MONEY))
    register(Currency("BWP", "Pula", 2, CurrencyType.MONEY))
    register(Currency("BYR", "Belarussian Ruble", 0, CurrencyType.MONEY))
    register(Currency("BZD", "Belize Dollar", 2, CurrencyType.MONEY))
    register(Currency("CAD", "Canadian Dollar", 2, CurrencyType.MONEY))
    register(Currency("CDF", "Congolese Franc", 2, CurrencyType.MONEY))
    register(Currency("CHE", "WIR Euro", 2, CurrencyType.MONEY))
    register(Currency("CHF", "Swiss Franc", 2, CurrencyType.MONEY))
    register(Currency("CHW", "WIR Franc", 2, CurrencyType.MONEY))
    register(Currency("CLF", "Unidad de Fomento", 4, CurrencyType.MONEY))
    register(Currency("CLP", "Chilean Peso", 0, CurrencyType.MONEY))
    register(Currency("CNH", "Yuan Renminbi (Off-shore)", 2, CurrencyType.MONEY))
    register(Currency("CNY", "Yuan Renminbi", 2, CurrencyType.MONEY))
    register(Currency("COP", "Colombian Peso", 2, CurrencyType.MONEY))
    register(Currency("COU", "Unidad de Valor Real", 2, CurrencyType.MONEY))
    register(Currency("CRC", "Costa Rican Colon", 2, CurrencyType.MONEY))
    register(Currency("CUC", "Peso Convertible", 2, CurrencyType.MONEY))
    register(Currency("CUP", "Cuban Peso", 2, CurrencyType.MONEY))
    register(Currency("CVE", "Cabo Verde Escudo", 2, CurrencyType.MONEY))
    register(Currency("CZK", "Czech Koruna", 2, CurrencyType.MONEY))
    register(Currency("DJF", "Djibouti Franc", 0, CurrencyType.MONEY))
    register(Currency("DKK", "Danish Krone", 2, CurrencyType.MONEY))
    register(Currency("DOP", "Dominican Peso", 2, CurrencyType.MONEY))
    register(Currency("DZD", "Algerian Dinar", 2, CurrencyType.MONEY))
    register(Currency("EGP", "Egyptian Pound", 2, CurrencyType.MONEY))
    register(Currency("ERN", "Nakfa", 2, CurrencyType.MONEY))
    register(Currency("ETB", "Ethiopian Birr", 2, CurrencyType.MONEY))
    register(Currency("EUR", "Euro", 2, CurrencyType.MONEY))
    register(Currency("FJD", "Fiji Dollar", 2, CurrencyType.MONEY))
    register(Currency("FKP", "Falkland Islands Pound", 2, CurrencyType.MONEY))
    register(Currency("GBP", "Pound Sterling", 2, CurrencyType.MONEY))
    register(Currency("GEL", "Lari", 2, CurrencyType.MONEY))
    register(Currency("GHS", "Ghana Cedi", 2, CurrencyType.MONEY))
    register(Currency("GIP", "Gibraltar Pound", 2, CurrencyType.MONEY))
    register(Currency("GMD", "Dalasi", 2, CurrencyType.MONEY))
    register(Currency("GNF", "Guinea Franc", 0, CurrencyType.MONEY))
    register(Currency("GTQ", "Quetzal", 2, CurrencyType.MONEY))
    register(Currency("GYD", "Guyana Dollar", 2, CurrencyType.MONEY))
    register(Currency("HKD", "Hong Kong Dollar", 2, CurrencyType.MONEY))
    register(Currency("HNL", "Lempira", 2, CurrencyType.MONEY))
    register(Currency("HRK", "Kuna", 2, CurrencyType.MONEY))
    register(Currency("HTG", "Gourde", 2, CurrencyType.MONEY))
    register(Currency("HUF", "Forint", 2, CurrencyType.MONEY))
    register(Currency("IDR", "Rupiah", 2, CurrencyType.MONEY))
    register(Currency("ILS", "New Israeli Sheqel", 2, CurrencyType.MONEY))
    register(Currency("INR", "Indian Rupee", 2, CurrencyType.MONEY))
    register(Currency("IQD", "Iraqi Dinar", 3, CurrencyType.MONEY))
    register(Currency("IRR", "Iranian Rial", 2, CurrencyType.MONEY))
    register(Currency("ISK", "Iceland Krona", 0, CurrencyType.MONEY))
    register(Currency("JMD", "Jamaican Dollar", 2, CurrencyType.MONEY))
    register(Currency("JOD", "Jordanian Dinar", 3, CurrencyType.MONEY))
    register(Currency("JPY", "Yen", 0, CurrencyType.MONEY))
    register(Currency("KES", "Kenyan Shilling", 2, CurrencyType.MONEY))
    register(Currency("KGS", "Som", 2, CurrencyType.MONEY))
    register(Currency("KHR", "Riel", 2, CurrencyType.MONEY))
    register(Currency("KMF", "Comoro Franc", 0, CurrencyType.MONEY))
    register(Currency("KPW", "North Korean Won", 2, CurrencyType.MONEY))
    register(Currency("KRW", "Won", 0, CurrencyType.MONEY))
    register(Currency("KWD", "Kuwaiti Dinar", 3, CurrencyType.MONEY))
    register(Currency("KYD", "Cayman Islands Dollar", 2, CurrencyType.MONEY))
    register(Currency("KZT", "Tenge", 2, CurrencyType.MONEY))
    register(Currency("LAK", "Kip", 2, CurrencyType.MONEY))
    register(Currency("LBP", "Lebanese Pound", 2, CurrencyType.MONEY))
    register(Currency("LKR", "Sri Lanka Rupee", 2, CurrencyType.MONEY))
    register(Currency("LRD", "Liberian Dollar", 2, CurrencyType.MONEY))
    register(Currency("LSL", "Loti", 2, CurrencyType.MONEY))
    register(Currency("LYD", "Libyan Dinar", 3, CurrencyType.MONEY))
    register(Currency("MAD", "Moroccan Dirham", 2, CurrencyType.MONEY))
    register(Currency("MDL", "Moldovan Leu", 2, CurrencyType.MONEY))
    register(Currency("MGA", "Malagasy Ariary", 2, CurrencyType.MONEY))
    register(Currency("MKD", "Denar", 2, CurrencyType.MONEY))
    register(Currency("MMK", "Kyat", 2, CurrencyType.MONEY))
    register(Currency("MNT", "Tugrik", 2, CurrencyType.MONEY))
    register(Currency("MOP", "Pataca", 2, CurrencyType.MONEY))
    register(Currency("MRO", "Ouguiya", 2, CurrencyType.MONEY))
    register(Currency("MUR", "Mauritius Rupee", 2, CurrencyType.MONEY))
    register(Currency("MVR", "Rufiyaa", 2, CurrencyType.MONEY))
    register(Currency("MWK", "Kwacha", 2, CurrencyType.MONEY))
    register(Currency("MXN", "Mexican Peso", 2, CurrencyType.MONEY))
    register(Currency("MXV", "Mexican Unidad de Inversion (UDI)", 2, CurrencyType.MONEY))
    register(Currency("MYR", "Malaysian Ringgit", 2, CurrencyType.MONEY))
    register(Currency("MZN", "Mozambique Metical", 2, CurrencyType.MONEY))
    register(Currency("NAD", "Namibia Dollar", 2, CurrencyType.MONEY))
    register(Currency("NGN", "Naira", 2, CurrencyType.MONEY))
    register(Currency("NIO", "Cordoba Oro", 2, CurrencyType.MONEY))
    register(Currency("NOK", "Norwegian Krone", 2, CurrencyType.MONEY))
    register(Currency("NPR", "Nepalese Rupee", 2, CurrencyType.MONEY))
    register(Currency("NZD", "New Zealand Dollar", 2, CurrencyType.MONEY))
    register(Currency("OMR", "Rial Omani", 3, CurrencyType.MONEY))
    register(Currency("PAB", "Balboa", 2, CurrencyType.MONEY))
    register(Currency("PEN", "Nuevo Sol", 2, CurrencyType.MONEY))
    register(Currency("PGK", "Kina", 2, CurrencyType.MONEY))
    register(Currency("PHP", "Philippine Peso", 2, CurrencyType.MONEY))
    register(Currency("PKR", "Pakistan Rupee", 2, CurrencyType.MONEY))
    register(Currency("PLN", "Zloty", 2, CurrencyType.MONEY))
    register(Currency("PYG", "Guarani", 0, CurrencyType.MONEY))
    register(Currency("QAR", "Qatari Rial", 2, CurrencyType.MONEY))
    register(Currency("RON", "Romanian Leu", 2, CurrencyType.MONEY))
    register(Currency("RSD", "Serbian Dinar", 2, CurrencyType.MONEY))
    register(Currency("RUB", "Russian Ruble", 2, CurrencyType.MONEY))
    register(Currency("RWF", "Rwanda Franc", 0, CurrencyType.MONEY))
    register(Currency("SAR", "Saudi Riyal", 2, CurrencyType.MONEY))
    register(Currency("SBD", "Solomon Islands Dollar", 2, CurrencyType.MONEY))
    register(Currency("SCR", "Seychelles Rupee", 2, CurrencyType.MONEY))
    register(Currency("SDG", "Sudanese Pound", 2, CurrencyType.MONEY))
    register(Currency("SEK", "Swedish Krona", 2, CurrencyType.MONEY))
    register(Currency("SGD", "Singapore Dollar", 2, CurrencyType.MONEY))
    register(Currency("SHP", "Saint Helena Pound", 2, CurrencyType.MONEY))
    register(Currency("SLL", "Leone", 2, CurrencyType.MONEY))
    register(Currency("SOS", "Somali Shilling", 2, CurrencyType.MONEY))
    register(Currency("SRD", "Surinam Dollar", 2, CurrencyType.MONEY))
    register(Currency("SSP", "South Sudanese Pound", 2, CurrencyType.MONEY))
    register(Currency("STD", "Dobra", 2, CurrencyType.MONEY))
    register(Currency("SVC", "El Salvador Colon", 2, CurrencyType.MONEY))
    register(Currency("SYP", "Syrian Pound", 2, CurrencyType.MONEY))
    register(Currency("SZL", "Lilangeni", 2, CurrencyType.MONEY))
    register(Currency("THB", "Baht", 2, CurrencyType.MONEY))
    register(Currency("TJS", "Somoni", 2, CurrencyType.MONEY))
    register(Currency("TMT", "Turkmenistan New Manat", 2, CurrencyType.MONEY))
    register(Currency("TND", "Tunisian Dinar", 3, CurrencyType.MONEY))
    register(Currency("TOP", "Pa'anga", 2, CurrencyType.MONEY))
    register(Currency("TRY", "Turkish Lira", 2, CurrencyType.MONEY))
    register(Currency("TTD", "Trinidad and Tobago Dollar", 2, CurrencyType.MONEY))
    register(Currency("TWD", "New Taiwan Dollar", 2, CurrencyType.MONEY))
    register(Currency("TZS", "Tanzanian Shilling", 2, CurrencyType.MONEY))
    register(Currency("UAH", "Hryvnia", 2, CurrencyType.MONEY))
    register(Currency("UGX", "Uganda Shilling", 0, CurrencyType.MONEY))
    register(Currency("USD", "US Dollar", 2, CurrencyType.MONEY))
    register(Currency("USN", "US Dollar (Next day)", 2, CurrencyType.MONEY))
    register(Currency("UYI", "Uruguay Peso en Unidades Indexadas", 0, CurrencyType.MONEY))
    register(Currency("UYU", "Peso Uruguayo", 2, CurrencyType.MONEY))
    register(Currency("UZS", "Uzbekistan Sum", 2, CurrencyType.MONEY))
    register(Currency("VEF", "Bolivar", 2, CurrencyType.MONEY))
    register(Currency("VND", "Dong", 0, CurrencyType.MONEY))
    register(Currency("VUV", "Vatu", 0, CurrencyType.MONEY))
    register(Currency("WST", "Tala", 2, CurrencyType.MONEY))
    register(Currency("XAG", "Silver", -1, CurrencyType.METAL))
    register(Currency("XAU", "Gold", -1, CurrencyType.METAL))
    register(Currency("XCD", "East Caribbean Dollar", 2, CurrencyType.MONEY))
    register(Currency("XPD", "Palladium", -1, CurrencyType.METAL))
    register(Currency("XPT", "Platinum", -1, CurrencyType.METAL))
    register(Currency("XSU", "Sucre", -1, CurrencyType.MONEY))
    register(Currency("XUA", "ADB Unit of Account", -1, CurrencyType.MONEY))
    register(Currency("YER", "Yemeni Rial", 2, CurrencyType.MONEY))
    register(Currency("ZAR", "Rand", 2, CurrencyType.MONEY))
    register(Currency("ZMW", "Zambian Kwacha", 2, CurrencyType.MONEY))
    register(Currency("ZWL", "Zimbabwe Dollar", 2, CurrencyType.MONEY))
