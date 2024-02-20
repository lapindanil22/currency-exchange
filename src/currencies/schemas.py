from pydantic import BaseModel, ConfigDict


class Currency(BaseModel):
    code: str
    name: str
    sign: str


class CurrencyWithID(Currency):
    id: int

    model_config = ConfigDict(from_attributes=True)
