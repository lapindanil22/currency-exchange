from pydantic import BaseModel


class Currency(BaseModel):
    code: str
    name: str
    sign: str


class CurrencyWithID(Currency):
    id: int

    # class Config:
    #     orm_mode = True
