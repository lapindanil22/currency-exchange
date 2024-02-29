from typing import Annotated

from fastapi import APIRouter, Body, Path
from fastapi.responses import JSONResponse

from exceptions import CurrencyNotFound, EntityExistsError, EntityNotFound, ExchangeRateNotFound

from .repository import ExchangeRateRepository
from .schemas import ExchangeRateWithCodePair, ExchangeRateWithCurrencies

router = APIRouter(
    prefix="/exchangeRates",
    tags=["Exchange Rates"]
)


@router.get("", response_model=list[ExchangeRateWithCurrencies])
async def get_exchange_rates():
    exchange_rates_dict = await ExchangeRateRepository.get_all()
    return exchange_rates_dict


@router.post("", response_model=ExchangeRateWithCurrencies)
async def post_exchange_rate(exchange_rate: Annotated[ExchangeRateWithCodePair, Body()]):
    try:
        exchange_rate_response = await ExchangeRateRepository.add(exchange_rate)
    except EntityExistsError:
        return JSONResponse(
            status_code=409,
            content={"message": "Валютная пара с таким кодом уже существует"}
        )
    except CurrencyNotFound:
        return JSONResponse(
            status_code=404,
            content={"message": "Одна (или обе) валюта из валютной пары не существует в БД"}
        )
    return exchange_rate_response


@router.get("/{exchange_pair}", response_model=ExchangeRateWithCurrencies)
async def get_exchange_rate(exchange_pair: Annotated[str, Path()]):
    base_currency_code = exchange_pair[:3]
    target_currency_code = exchange_pair[3:]

    try:
        exchange_rate = await ExchangeRateRepository.get_by_pair(base_currency_code,
                                                                 target_currency_code)
    except ExchangeRateNotFound:
        return JSONResponse(status_code=404,
                            content={"message": "Exchange rate for this pair not found"})
    return exchange_rate


@router.patch("/{exchange_pair}", response_model=ExchangeRateWithCurrencies)
async def patch_exchange_rate(exchange_pair: Annotated[str, Path()],
                              new_rate: Annotated[float, Body()]):
    base_currency_code = exchange_pair[:3]
    target_currency_code = exchange_pair[3:]

    try:
        exchange_rate = await ExchangeRateRepository.patch_by_pair(
            base_currency_code,
            target_currency_code,
            new_rate
        )
    except EntityNotFound:
        return JSONResponse(
            # 404 / 404 respectively
            status_code=404,
            content={"message": "Валютная пара отсутствует в базе данных / Обменный курс для пары не найден"}
        )
    return exchange_rate


@router.delete("/{exchange_pair}", response_model=ExchangeRateWithCurrencies)
async def delete_currency(exchange_pair: Annotated[str, Path()]):
    base_currency_code = exchange_pair[:3]
    target_currency_code = exchange_pair[3:]

    exchange_rate = await ExchangeRateRepository.delete_by_pair(
        base_currency_code,
        target_currency_code
    )

    if exchange_rate is None:
        return JSONResponse(
            status_code=404,
            content={"message": "Обменный курс для пары не найден"}
        )

    return exchange_rate
