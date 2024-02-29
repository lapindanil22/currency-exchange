from typing import Optional

from sqlalchemy import select

from database import async_session_maker
from exceptions import CurrencyNotFound, EntityExistsError

from .models import CurrencyORM
from .schemas import Currency, CurrencyWithID


class CurrencyRepository:
    @classmethod
    async def get_all(cls) -> list[CurrencyWithID]:
        async with async_session_maker() as session:
            query = select(CurrencyORM)
            result = await session.execute(query)

            currencies_orm = result.scalars().all()
            currencies = [
                CurrencyWithID.model_validate(currency_orm) for currency_orm in currencies_orm
            ]
            return currencies

    @classmethod
    async def add(cls, data: Currency) -> Optional[CurrencyWithID]:
        async with async_session_maker() as session:
            query = select(CurrencyORM).filter(CurrencyORM.code == data.code)
            result = await session.execute(query)

            if result.scalar_one_or_none() is not None:
                raise EntityExistsError("Currency with this code already exists")

            currency_dict = data.model_dump()
            currency_orm = CurrencyORM(**currency_dict)

            session.add(currency_orm)
            await session.flush()
            await session.commit()
            return currency_orm

    @classmethod
    async def get_by_code(cls, code: str) -> Optional[CurrencyWithID]:
        async with async_session_maker() as session:
            query = select(CurrencyORM).filter(CurrencyORM.code == code)
            result = await session.execute(query)
            currency_orm = result.scalar_one_or_none()

            if currency_orm is None:
                raise CurrencyNotFound

            currency = CurrencyWithID.model_validate(currency_orm)
            return currency

    @classmethod
    async def get_by_id(cls, id: int) -> Optional[CurrencyWithID]:
        async with async_session_maker() as session:
            query = select(CurrencyORM).filter(CurrencyORM.id == id)
            result = await session.execute(query)
            currency_orm = result.scalar_one_or_none()

            if currency_orm is None:
                return None

            currency = CurrencyWithID.model_validate(currency_orm)
            return currency

    @classmethod
    async def delete(cls, code: str) -> Optional[CurrencyWithID]:
        async with async_session_maker() as session:
            query = select(CurrencyORM).filter(CurrencyORM.code == code)
            result = await session.execute(query)
            currency = result.scalar_one_or_none()

            if currency is None:
                return None

            await session.delete(currency)
            await session.commit()
            return currency
