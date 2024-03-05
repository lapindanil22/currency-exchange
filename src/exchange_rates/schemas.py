from pydantic import BaseModel, ConfigDict

from currencies.schemas import CurrencyWithID


class _ExchangeRate(BaseModel):
    rate: float


class ExchangeRate(_ExchangeRate):
    baseCurrencyCode: str
    targetCurrencyCode: str


class ExchangeRateWithCurrencies(_ExchangeRate):
    base_currency: CurrencyWithID
    target_currency: CurrencyWithID


class ExchangeRateWithID(_ExchangeRate):
    base_currency_id: int
    target_currency_id: int

    model_config = ConfigDict(from_attributes=True)
