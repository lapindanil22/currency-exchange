from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import aliased

from currencies.models import CurrencyORM
from currencies.repository import CurrencyRepository
from currencies.schemas import CurrencyWithID
from database import async_session_maker

from .models import ExchangeRateORM
from .schemas import ExchangeRateWithCodePair, ExchangeRateWithCurrencies, ExchangeRateWithID


class ExchangeRateRepository:
    @classmethod
    async def get_all(cls) -> list[ExchangeRateWithCurrencies]:
        async with async_session_maker() as session:
            query = select(ExchangeRateORM)
            result = await session.execute(query)
            exchange_rates_orm = result.scalars().all()
            exchange_rates = [
                ExchangeRateWithID.model_validate(exchange_rate) for exchange_rate in exchange_rates_orm
            ]

            exchange_rates_response: list[ExchangeRateWithCurrencies] = []

            for exchange_rate in exchange_rates:
                query = select(CurrencyORM).filter(
                    CurrencyORM.id == int(exchange_rate.base_currency_id))
                result = await session.execute(query)
                base_currency_orm = result.scalar_one()
                base_currency = CurrencyWithID.model_validate(base_currency_orm)

                query = select(CurrencyORM).filter(
                    CurrencyORM.id == int(exchange_rate.target_currency_id))
                result = await session.execute(query)
                target_currency_orm = result.scalar_one()
                target_currency = CurrencyWithID.model_validate(target_currency_orm)

                exchange_rate_response = ExchangeRateWithCurrencies(
                    rate=exchange_rate.rate,
                    base_currency=base_currency,
                    target_currency=target_currency
                )

                exchange_rates_response.append(exchange_rate_response)

            return exchange_rates_response

    @classmethod
    async def add(cls,
                  exchange_rate: ExchangeRateWithCodePair) -> Optional[ExchangeRateWithCurrencies]:
        async with async_session_maker() as session:
            base_currency = await CurrencyRepository.get_by_code(exchange_rate.baseCurrencyCode)
            target_currency = await CurrencyRepository.get_by_code(exchange_rate.targetCurrencyCode)

            if base_currency is None or target_currency is None:
                # TODO Exception handling
                # 404 - Одна (или обе) валюта из валютной пары не существует в БД
                return None

            exchange_rate_check = await ExchangeRateRepository.get_by_pair(
                exchange_rate.baseCurrencyCode,
                exchange_rate.targetCurrencyCode
            )
            if exchange_rate_check is not None:
                # 409 - Валютная пара с таким кодом уже существует
                return None

            exchange_rate_orm = ExchangeRateORM(
                base_currency_id=base_currency.id,
                target_currency_id=target_currency.id,
                rate=exchange_rate.rate
            )
            session.add(exchange_rate_orm)
            await session.flush()
            await session.commit()

            exchange_rate_response = ExchangeRateWithCurrencies(
                base_currency=base_currency,
                target_currency=target_currency,
                rate=exchange_rate.rate
            )

            return exchange_rate_response

    @classmethod
    async def get_by_pair(cls,
                          base_currency_code,
                          target_currency_code) -> Optional[ExchangeRateWithCurrencies]:
        async with async_session_maker() as session:
            base_currency_alias = aliased(CurrencyORM)
            target_curency_alias = aliased(CurrencyORM)

            query = select(ExchangeRateORM) \
                .join(base_currency_alias,
                      ExchangeRateORM.base_currency_id == base_currency_alias.id) \
                .join(target_curency_alias,
                      ExchangeRateORM.target_currency_id == target_curency_alias.id) \
                .filter(base_currency_alias.code == base_currency_code,
                        target_curency_alias.code == target_currency_code)

            result = await session.execute(query)

            exchange_rate_orm = result.scalar_one_or_none()

            if exchange_rate_orm is None:
                return None

            exchange_rate = ExchangeRateWithID.model_validate(exchange_rate_orm)

            query = select(CurrencyORM).filter(
                CurrencyORM.id == int(exchange_rate.base_currency_id))
            result = await session.execute(query)
            base_currency_orm = result.scalar_one()
            base_currency = CurrencyWithID.model_validate(base_currency_orm)

            query = select(CurrencyORM).filter(
                CurrencyORM.id == int(exchange_rate.target_currency_id))
            result = await session.execute(query)
            target_currency_orm = result.scalar_one()
            target_currency = CurrencyWithID.model_validate(target_currency_orm)

            exchange_rate_response = ExchangeRateWithCurrencies(
                rate=exchange_rate.rate,
                base_currency=base_currency,
                target_currency=target_currency
            )

            return exchange_rate_response

    @classmethod
    async def patch_by_pair(cls,
                            base_currency_code,
                            target_currency_code,
                            new_rate) -> Optional[ExchangeRateWithCurrencies]:
        async with async_session_maker() as session:
            base_currency = await CurrencyRepository.get_by_code(base_currency_code)
            target_currency = await CurrencyRepository.get_by_code(target_currency_code)

            if base_currency is None or target_currency is None:
                # 404 - Валютная пара отсутствует в базе данных
                return None

            exchange_rate_with_currencies = await ExchangeRateRepository.get_by_pair(
                base_currency_code,
                target_currency_code
            )

            if exchange_rate_with_currencies is None:
                # 404 - Обменный курс для пары не найден
                return None

            query = select(ExchangeRateORM).filter(
                ExchangeRateORM.base_currency_id == exchange_rate_with_currencies.base_currency.id,
                ExchangeRateORM.target_currency_id == exchange_rate_with_currencies.target_currency.id
            )
            result = await session.execute(query)
            exchange_rate_orm = result.scalar_one()

            exchange_rate_orm.rate = Decimal(new_rate)
            # await session.flush()
            await session.commit()

            exchange_rate_with_currencies = await ExchangeRateRepository.get_by_pair(
                base_currency_code,
                target_currency_code
            )

            return exchange_rate_with_currencies

    @classmethod
    async def delete_by_pair(cls,
                             base_currency_code,
                             target_currency_code) -> Optional[ExchangeRateWithCurrencies]:
        async with async_session_maker() as session:
            exchange_rate = await ExchangeRateRepository.get_by_pair(
                base_currency_code,
                target_currency_code
            )

            if exchange_rate is None:
                # 404 - Обменный курс для пары не найден
                return None

            base_currency_alias = aliased(CurrencyORM)
            target_curency_alias = aliased(CurrencyORM)

            query = select(ExchangeRateORM) \
                .join(base_currency_alias,
                      ExchangeRateORM.base_currency_id == base_currency_alias.id) \
                .join(target_curency_alias,
                      ExchangeRateORM.target_currency_id == target_curency_alias.id) \
                .filter(base_currency_alias.code == base_currency_code,
                        target_curency_alias.code == target_currency_code)

            result = await session.execute(query)

            exchange_rate_orm = result.scalar_one_or_none()

            await session.delete(exchange_rate_orm)
            await session.commit()

            return exchange_rate
