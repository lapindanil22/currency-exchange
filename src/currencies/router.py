from typing import Annotated

from fastapi import APIRouter, Body, Path
from fastapi.responses import JSONResponse

from repository import CurrencyRepository

from .schemas import Currency, CurrencyWithID

router = APIRouter(
    prefix="/currencies",
    tags=["Currencies"]
)


@router.get("", response_model=list[CurrencyWithID])
def get_currencies():
    currencies = CurrencyRepository.get_all()
    return currencies


@router.post("", response_model=CurrencyWithID)
def post_currency(currency: Annotated[Currency, Body()]):
    currency_with_id = CurrencyRepository.add(currency)
    if currency_with_id is None:
        return JSONResponse(status_code=409,
                            content={"message": "Валюта с таким кодом уже существует"})
    return currency_with_id


@router.get("/{code}", response_model=CurrencyWithID)
def get_currency_empty(code: Annotated[str, Path()]):
    currency = CurrencyRepository.get_by_code(code=code)
    if currency is None:
        return JSONResponse(status_code=404, content={"message": "Валюта не найдена"})
    return currency


@router.delete("/{code}", response_model=CurrencyWithID)
def delete_currency(code: Annotated[str, Path()]):
    currency = CurrencyRepository.delete(code=code)
    if currency is None:
        return JSONResponse(status_code=404,
                            content={"message": "Валюта не найдена"})
    return currency
