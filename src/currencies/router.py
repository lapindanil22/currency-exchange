from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from .schema import Currency, CurrencyBase
from .model import CurrencyModel
from src.database import get_db

router = APIRouter(
    prefix="/currencies",
    tags=["Currencies"]
)


@router.get("", response_model=list[Currency])
def get_currencies(db: Session = Depends(get_db)):
    return db.query(CurrencyModel).all()


@router.post("", response_model=Currency)  # TODO right response_model?
def post_currency(currency: Annotated[CurrencyBase, Body()],
                  db: Session = Depends(get_db)):
    if db.query(CurrencyModel).filter(CurrencyModel.code == currency.code).first():
        return JSONResponse(status_code=409,
                            content={"message": "Валюта с таким кодом уже существует"})
    currency_model = CurrencyModel(**currency.model_dump())
    db.add(currency_model)
    db.commit()
    db.refresh(currency_model)
    return currency_model


@router.get("/{code}", response_model=Currency)
def get_currency_empty(code: Annotated[str, Path()],
                       db: Session = Depends(get_db)):
    currency = db.query(CurrencyModel).filter(CurrencyModel.code == code).first()
    if not currency:
        return JSONResponse(status_code=404, content={"message": "Валюта не найдена"})
    return currency


@router.delete("/{code}", response_model=Currency)
def delete_currency(code: Annotated[str, Path()],
                    db: Session = Depends(get_db)):
    currency = db.query(CurrencyModel).filter(CurrencyModel.code == code).first()
    if not currency:
        return JSONResponse(status_code=404,
                            content={"message": "Валюта не найдена"})
    db.delete(currency)
    db.commit()
    return currency
