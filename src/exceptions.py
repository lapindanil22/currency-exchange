class EntityExistsError(BaseException):
    pass


class EntityNotFound(BaseException):
    pass


class CurrencyNotFound(EntityNotFound):
    pass


class ExchangeRateNotFound(EntityNotFound):
    pass
