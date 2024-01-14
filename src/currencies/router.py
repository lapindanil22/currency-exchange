from typing import Annotated
from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from src.currencies.models import Currency
from src.database import get_db


router = APIRouter(
    prefix="/currencies",
    tags=["Currencies"]
)


@router.get("")
def get_currencies(db: Session = Depends(get_db)):
    return db.query(Currency).all()


@router.get("/{code}")
def get_currency_empty(code: Annotated[str, Path()],
                       db: Session = Depends(get_db)):
    currency = db.query(Currency).filter(Currency.code == code).first()
    if not currency:
        return JSONResponse(status_code=404, content={"message": "Валюта не найдена"})
    return currency


@router.post("")
def post_currency(name: Annotated[str, Body()],
                  code: Annotated[str, Body()],
                  sign: Annotated[str, Body()],
                  db: Session = Depends(get_db)):
    if db.query(Currency).filter(Currency.code == code).first():
        return JSONResponse(status_code=409,
                            content={"message": "Валюта с таким кодом уже существует"})
    currency = Currency(name=name, code=code, sign=sign)
    db.add(currency)
    db.commit()
    db.refresh(currency)
    return currency


@router.delete("/{code}")
def delete_currency(code: Annotated[str, Path()],
                    db: Session = Depends(get_db)):
    currency = db.query(Currency).filter(Currency.code == code).first()
    if not currency:
        return JSONResponse(status_code=404,
                            content={"message": "Валюта не найдена"})
    db.delete(currency)
    db.commit()
    return currency
