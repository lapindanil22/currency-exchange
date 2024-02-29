from pydantic import BaseModel

from currencies.schemas import Currency


class Exchange(BaseModel):
    base_currency: Currency
    target_currency: Currency
    rate: float
    amount: float
    converted_amount: float
