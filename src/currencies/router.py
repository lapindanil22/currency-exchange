from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from repository import CurrencyRepository

from .schemas import CurrencyWithID, Currency
from .models import CurrencyORM
from database import get_db

router = APIRouter(
    prefix="/currencies",
    tags=["Currencies"]
)


@router.get("", response_model=list[CurrencyWithID])
def get_currencies(db: Session = Depends(get_db)):
    currencies = CurrencyRepository.get_all()
    return currencies


@router.post("", response_model=CurrencyWithID)
def post_currency(currency: Annotated[Currency, Body()],
                  db: Session = Depends(get_db)):
    currency_with_id = CurrencyRepository.add(currency)
    if currency_with_id is None:
        return JSONResponse(status_code=409,
                            content={"message": "Валюта с таким кодом уже существует"})
    return currency_with_id


@router.get("/{code}", response_model=CurrencyWithID)
def get_currency_empty(code: Annotated[str, Path()],
                       db: Session = Depends(get_db)):
    currency = db.query(CurrencyORM).filter(CurrencyORM.code == code).first()
    if not currency:
        return JSONResponse(status_code=404, content={"message": "Валюта не найдена"})
    return currency


@router.delete("/{code}", response_model=CurrencyWithID)
def delete_currency(code: Annotated[str, Path()],
                    db: Session = Depends(get_db)):
    currency = db.query(CurrencyORM).filter(CurrencyORM.code == code).first()
    if not currency:
        return JSONResponse(status_code=404,
                            content={"message": "Валюта не найдена"})
    db.delete(currency)
    db.commit()
    return currency
