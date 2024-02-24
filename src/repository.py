from typing import Optional

from currencies.models import CurrencyORM
from currencies.schemas import Currency, CurrencyWithID
from database import SessionLocal


class CurrencyRepository:
    @classmethod
    def get_all(cls) -> list[CurrencyWithID]:
        with SessionLocal() as session:
            currencies_orm = session.query(CurrencyORM).all()
            currencies = [CurrencyWithID.model_validate(currency_orm) for currency_orm in currencies_orm]
            return currencies

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

    @classmethod
    def get_by_code(cls, code: str) -> Optional[CurrencyWithID]:
        with SessionLocal() as session:
            currency_orm = session.query(CurrencyORM).filter(CurrencyORM.code == code).first()
            if currency_orm is None:
                return None
            currency = CurrencyWithID.model_validate(currency_orm)
            return currency

    @classmethod
    def delete(cls, code: str) -> Optional[CurrencyWithID]:
        with SessionLocal() as session:
            currency = session.query(CurrencyORM).filter(CurrencyORM.code == code).first()
            if currency is None:
                return None
            session.delete(currency)
            session.commit()
            return currency


# class ExchangeRateRepository:
#     @classmethod
#     def get_all(cls) -> list[ExchangeRate]:
#         with SessionLocal() as session:
#             exchange_rates_orm = session.query(ExchangeRateORM).all()
#             exchange_rates = [ExchangeRate.model_validate(exchange_rate_orm) for exchange_rate_orm in exchange_rates_orm]
#             return exchange_rates

#     @classmethod
#     def add(cls, data: ExchangeRateRequest) -> Optional[ExchangeRateResponse]:
#         with SessionLocal() as session:
#             base_currency = session.query(ExchangeRateORM).filter(ExchangeRateORM.code == data.base_currency_code).first()
#             target_currency = session.query(ExchangeRateORM).filter(ExchangeRateORM.code == data.target_currency_code).first()
#             if base_currency is None or target_currency is None:
#                 return None
#             exchange_rate_dict = data.model_dump()
#             exchange_rate_orm = ExchangeRateORM(**exchange_rate_dict)
#             session.add(exchange_rate_orm)
#             session.commit()
#             session.refresh(exchange_rate_orm)
#             return exchange_rate_orm

    # @classmethod
    # def get_by_code(cls, pair: str) -> Optional[ExchangeRateResponse]:
    #     with SessionLocal() as session:
    #         exchange_rate_orm = session.query(ExchangeRateORM).filter(ExchangeRateORM.code == pair).first()
    #         if exchange_rate_orm is None:
    #             return None
    #         currency = CurrencyWithID.model_validate(exchange_rate_orm)
    #         return currency

    # @classmethod
    # def delete(cls, code: str) -> Optional[CurrencyWithID]:
    #     with SessionLocal() as session:
    #         currency = session.query(ExchangeRateORM).filter(ExchangeRateORM.code == code).first()
    #         if currency is None:
    #             return None
    #         session.delete(currency)
    #         session.commit()
    #         return currency
