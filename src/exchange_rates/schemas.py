from pydantic import BaseModel

from currencies.schemas import CurrencyWithID


class _ExchangeRateBase(BaseModel):
    rate: float  # TODO make Decimal?


class ExchangeRateResponse(_ExchangeRateBase):
    base_currency: CurrencyWithID
    target_currency: CurrencyWithID


class ExchangeRate(_ExchangeRateBase):
    id: int
    base_currency_id: int
    target_currency_id: int

    # class Config:
    #     orm_mode = True
