from pydantic import BaseModel


class CurrencyBase(BaseModel):
    code: str
    name: str
    sign: str


class Currency(CurrencyBase):
    id: int

    # class Config:
    #     orm_mode = True
