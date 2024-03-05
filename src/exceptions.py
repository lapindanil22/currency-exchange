class EntityExistsError(BaseException):
    pass


class _EntityNotFound(BaseException):
    pass


class CurrencyNotFound(_EntityNotFound):
    pass


class ExchangeRateNotFound(_EntityNotFound):
    pass
