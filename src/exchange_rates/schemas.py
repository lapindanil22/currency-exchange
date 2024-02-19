from pydantic import BaseModel

from currencies.schemas import Currency


class ExchangeRateBase(BaseModel):
    rate: float  # TODO make Decimal?


# class ExchangeRate


class ExchangeRateResponse(ExchangeRateBase):
    base_currency: Currency
    target_currency: Currency


class ExchangeRate(ExchangeRateBase):
    id: int
    base_currency_id: int
    target_currency_id: int

    # class Config:
    #     orm_mode = True
