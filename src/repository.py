from typing import Optional
from currencies.models import CurrencyORM
from currencies.schemas import Currency, CurrencyWithID
from database import SessionLocal


class CurrencyRepository:
    @classmethod
    def add(cls, data: Currency) -> Optional[CurrencyWithID]:
        with SessionLocal() as session:
            if session.query(CurrencyORM).filter(CurrencyORM.code == data.code).first():
                return None

            currency_dict = data.model_dump()
            currency_orm = CurrencyORM(**currency_dict)
            session.add(currency_orm)
            session.commit()
            session.refresh(currency_orm)
            return currency_orm
