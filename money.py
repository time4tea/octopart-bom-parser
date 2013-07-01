from decimal import Decimal


class Wallet:

    def __init__(self):
        self._wallet = {}

    def __add__(self, money):
        existing = self._wallet.get(money._currency, Money(0, money._currency))
        self._wallet[money._currency] = existing + money

    def __sub__(self, money):
        existing = self._wallet.get(money._currency, Money(0, money._currency))
        self._wallet[money._currency] = existing - money

    def __iter__(self):
        return self._wallet.itervalues()


class Currency:

    def __init__(self, iso):
        self._iso = iso

    def __str__(self):
        return self._iso

    def __eq__(self, other):
        return self._iso == other._iso

    def __hash__(self):
        return self._iso.__hash__()


class Money:

    def __init__(self, amount, currency):
        if not isinstance(amount, Decimal):
            amount = Decimal(str(amount or 0))
        self._amount = amount
        if not isinstance(currency, Currency):
            currency = Currency(currency)
        self._currency = currency

    def __str__(self):
        return str(self._currency) + str(self._amount)

    def in_currency_of(self, other):
        return self._currency == other._currency

    def check_currency(self, other):
        if not self.in_currency_of(other):
            raise ValueError("Can't add money amounts of %s and %s" % ( self, other ))

    def __add__(self, other):
        self.check_currency(other)
        return Money(self._amount + other._amount, self._currency)

    def __sub__(self, other):
        self.check_currency(other)
        return Money(self._amount - other._amount, self._currency)

    def __mul__(self, scalar):
        if not isinstance(scalar, Decimal):
            scalar = Decimal(scalar)
        return Money(self._amount * scalar, self._currency)

    def __div__(self, scalar):
        if not isinstance(scalar, Decimal):
            scalar = Decimal(scalar)
        return Money(self._amount / scalar, self._currency)




