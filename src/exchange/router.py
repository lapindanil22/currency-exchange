from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from exceptions import ExchangeRateNotFound
from exchange.schemas import Exchange
from exchange_rates.repository import ExchangeRateRepository

router = APIRouter(
    prefix="/exchange",
    tags=["Exchange"]
)


@router.get("", response_model=Exchange)
async def get_exchange(baseCode: Annotated[str, Query()],
                       targetCode: Annotated[str, Query()],
                       amount: Annotated[float, Query()]):
    try:
        exchange_rate = await ExchangeRateRepository.get_by_pair(baseCode, targetCode)
    except ExchangeRateNotFound:
        return JSONResponse(
            status_code=404,
            content={"message": "Обменный курс для пары не найден"}
        )

    exchange_dict = {
        "base_currency": exchange_rate.base_currency,
        "target_currency": exchange_rate.target_currency,
        "rate": exchange_rate.rate,
        "amount": amount,
        "converted_amount": round(float(exchange_rate.rate) * amount, 2)
    }

    return exchange_dict
