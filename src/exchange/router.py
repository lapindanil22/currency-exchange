from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession

from currencies.models import CurrencyORM
from database import get_async_session
from exchange_rates.models import ExchangeRateORM

router = APIRouter(
    prefix="/exchange",
    tags=["Exchange"]
)


@router.get("")
async def get_exchange(baseCode: Annotated[str, Query()],
                       targetCode: Annotated[str, Query()],
                       amount: Annotated[float, Query()],
                       session: AsyncSession = Depends(get_async_session)):
    query = select(CurrencyORM).filter(CurrencyORM.code == baseCode)
    result = await session.execute(query)
    base_currency = result.scalar_one_or_none()

    query = select(CurrencyORM).filter(CurrencyORM.code == targetCode)
    result = await session.execute(query)
    target_currency = result.scalar_one_or_none()

    if base_currency is None or target_currency is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Одна (или обе) валюта из валютной пары не существует в БД"}
        )

    c1 = aliased(CurrencyORM)
    c2 = aliased(CurrencyORM)

    query = select(ExchangeRateORM) \
        .join(c1, ExchangeRateORM.base_currency_id == c1.id) \
        .join(c2, ExchangeRateORM.target_currency_id == c2.id) \
        .filter(c1.code == baseCode, c2.code == targetCode)
    result = await session.execute(query)
    exchange_rate = result.scalar_one_or_none()

    if exchange_rate is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Обменный курс для пары не найден"}
        )

    query = select(CurrencyORM).filter(CurrencyORM.code == baseCode)
    result = await session.execute(query)
    base_currency = result.scalar_one()

    query = select(CurrencyORM).filter(CurrencyORM.code == targetCode)
    result = await session.execute(query)
    target_currency = result.scalar_one()

    base_currency_dict = base_currency.__dict__.copy()
    target_currency_dict = target_currency.__dict__.copy()

    exchange_dict = {
        "base_currency": base_currency_dict,
        "target_currency": target_currency_dict,
        "rate": exchange_rate.rate,
        "amount": amount,
        "converted_amount": round(float(exchange_rate.rate) * amount, 2)
    }

    return exchange_dict
