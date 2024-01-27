from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, aliased

from src.currencies.model import CurrencyModel
from src.database import get_db
from .schema import ExchangeRateResponse
from .model import ExchangeRateModel

router = APIRouter(
    prefix="/exchangeRates",
    tags=["Exchange Rates"]
)


@router.get("", response_model=list[ExchangeRateResponse])
def get_exchange_rates(db: Session = Depends(get_db)):
    exchange_rates = db.query(ExchangeRateModel).all()
    exchange_rates_dict = [exchange_rate.__dict__.copy() for exchange_rate in exchange_rates]

    for exchange_rate in exchange_rates_dict:
        base_currency = db.query(CurrencyModel).filter(
            CurrencyModel.id == int(exchange_rate["base_currency_id"])).first()
        target_currency = db.query(CurrencyModel).filter(
            CurrencyModel.id == int(exchange_rate["target_currency_id"])).first()
        exchange_rate["base_currency"] = base_currency.__dict__.copy()
        exchange_rate["target_currency"] = target_currency.__dict__.copy()
        exchange_rate["rate"] = round(float(exchange_rate["rate"]), 2)

        del exchange_rate["base_currency_id"]
        del exchange_rate["target_currency_id"]
        del exchange_rate["_sa_instance_state"]
        del exchange_rate["base_currency"]["_sa_instance_state"]
        del exchange_rate["target_currency"]["_sa_instance_state"]

    return exchange_rates_dict


@router.post("", response_model=ExchangeRateResponse)
def post_exchange_rate(baseCurrencyCode: Annotated[str, Body()],
                       targetCurrencyCode: Annotated[str, Body()],
                       rate: Annotated[float, Body()],
                       db: Session = Depends(get_db)):
    base_currency = db.query(CurrencyModel).filter(CurrencyModel.code == baseCurrencyCode).first()
    target_currency = db.query(CurrencyModel).filter(CurrencyModel.code == targetCurrencyCode).first()
    if not base_currency or not target_currency:
        return JSONResponse(
            status_code=404,
            content={"message": "Одна (или обе) валюта из валютной пары не существует в БД"}
        )

    if db.query(ExchangeRateModel).filter(ExchangeRateModel.base_currency_id == base_currency.id,
                                     ExchangeRateModel.target_currency_id == target_currency.id).first():
        return JSONResponse(status_code=409,
                            content={"message": "Валютная пара с таким кодом уже существует"})

    base_currency_dict = base_currency.__dict__.copy()
    target_currency_dict = target_currency.__dict__.copy()

    exchange_rate_model = ExchangeRateModel(base_currency_id=base_currency.id,
                                 target_currency_id=target_currency.id,
                                 rate=rate)
    db.add(exchange_rate_model)
    db.commit()
    db.refresh(exchange_rate_model)

    exchange_rate_model_dict = exchange_rate_model.__dict__.copy()

    exchange_rate_model_dict["rate"] = round(float(exchange_rate_model_dict["rate"]), 2)

    del exchange_rate_model_dict["_sa_instance_state"]
    del base_currency_dict["_sa_instance_state"]
    del target_currency_dict["_sa_instance_state"]

    exchange_rate_model_dict.pop("base_currency_id")
    exchange_rate_model_dict.pop("target_currency_id")

    exchange_rate_model_dict["base_currency"] = base_currency_dict
    exchange_rate_model_dict["target_currency"] = target_currency_dict

    return exchange_rate_model_dict


@router.get("/{exchange_pair}", response_model=ExchangeRateResponse)
def get_exchange_rate(exchange_pair: Annotated[str, Path()],
                      db: Session = Depends(get_db)):
    base_currency_code = exchange_pair[:3]
    target_currency_code = exchange_pair[3:]

    c1 = aliased(CurrencyModel)
    c2 = aliased(CurrencyModel)
    exchange_rate = db.query(ExchangeRateModel) \
        .join(c1, ExchangeRateModel.base_currency_id == c1.id) \
        .join(c2, ExchangeRateModel.target_currency_id == c2.id) \
        .filter(c1.code == base_currency_code, c2.code == target_currency_code).first()

    if not exchange_rate:
        return JSONResponse(status_code=404,
                            content={"message": "Обменный курс для пары не найден"})

    exchange_rate_dict = exchange_rate.__dict__.copy()
    del exchange_rate_dict["_sa_instance_state"]

    base_currency = db.query(CurrencyModel).filter(
            CurrencyModel.id == int(exchange_rate_dict["base_currency_id"])).first()
    target_currency = db.query(CurrencyModel).filter(
            CurrencyModel.id == int(exchange_rate_dict["target_currency_id"])).first()

    exchange_rate_dict["base_currency"] = base_currency.__dict__.copy()
    del exchange_rate_dict["base_currency"]["_sa_instance_state"]
    del exchange_rate_dict["base_currency_id"]

    exchange_rate_dict["target_currency"] = target_currency.__dict__.copy()
    del exchange_rate_dict["target_currency"]["_sa_instance_state"]
    del exchange_rate_dict["target_currency_id"]

    exchange_rate_dict["rate"] = round(float(exchange_rate_dict["rate"]), 2)

    return exchange_rate_dict


@router.patch("/{exchange_pair}", response_model=ExchangeRateResponse)
def patch_exchange_rate(exchange_pair: Annotated[str, Path()],
                        rate: Annotated[float, Body()],
                        db: Session = Depends(get_db)):
    base_currency_code = exchange_pair[:3]
    target_currency_code = exchange_pair[3:]

    base_currency = db.query(CurrencyModel).filter(CurrencyModel.code == base_currency_code).first()
    target_currency = db.query(CurrencyModel).filter(CurrencyModel.code == target_currency_code).first()
    if not base_currency or not target_currency:
        return JSONResponse(
            status_code=404,
            content={"message": "Валютная пара отсутствует в базе данных"}
        )

    c1 = aliased(CurrencyModel)
    c2 = aliased(CurrencyModel)

    base_currency_dict = base_currency.__dict__.copy()
    target_currency_dict = target_currency.__dict__.copy()

    exchange_rate = db.query(ExchangeRateModel) \
        .join(c1, ExchangeRateModel.base_currency_id == c1.id) \
        .join(c2, ExchangeRateModel.target_currency_id == c2.id) \
        .filter(c1.code == base_currency_code, c2.code == target_currency_code).first()
    if not exchange_rate:
        return JSONResponse(
            status_code=404,
            content={"message": "Обменный курс для пары не найден"}
        )

    exchange_rate.rate = rate
    db.commit()
    db.refresh(exchange_rate)

    exchange_rate_dict = exchange_rate.__dict__.copy()

    exchange_rate_dict["rate"] = round(float(exchange_rate_dict["rate"]), 2)

    del exchange_rate_dict["_sa_instance_state"]
    del base_currency_dict["_sa_instance_state"]
    del target_currency_dict["_sa_instance_state"]

    exchange_rate_dict.pop("base_currency_id")
    exchange_rate_dict.pop("target_currency_id")

    exchange_rate_dict["base_currency"] = base_currency_dict
    exchange_rate_dict["target_currency"] = target_currency_dict

    return exchange_rate_dict


@router.delete("/{exchange_pair}", response_model=ExchangeRateResponse)
def delete_currency(exchange_pair: Annotated[str, Path()],
                    db: Session = Depends(get_db)):
    base_currency_code = exchange_pair[:3]
    target_currency_code = exchange_pair[3:]

    c1 = aliased(CurrencyModel)
    c2 = aliased(CurrencyModel)
    exchange_rate = db.query(ExchangeRateModel) \
        .join(c1, ExchangeRateModel.base_currency_id == c1.id) \
        .join(c2, ExchangeRateModel.target_currency_id == c2.id) \
        .filter(c1.code == base_currency_code, c2.code == target_currency_code).first()

    if not exchange_rate:
        return JSONResponse(status_code=404,
                            content={"message": "Обменный курс для пары не найден"})

    db.delete(exchange_rate)
    db.commit()

    exchange_rate_dict = exchange_rate.__dict__.copy()
    del exchange_rate_dict["_sa_instance_state"]

    base_currency = db.query(CurrencyModel).filter(
            CurrencyModel.id == int(exchange_rate_dict["base_currency_id"])).first()
    target_currency = db.query(CurrencyModel).filter(
            CurrencyModel.id == int(exchange_rate_dict["target_currency_id"])).first()

    exchange_rate_dict["base_currency"] = base_currency.__dict__.copy()
    del exchange_rate_dict["base_currency"]["_sa_instance_state"]
    del exchange_rate_dict["base_currency_id"]

    exchange_rate_dict["target_currency"] = target_currency.__dict__.copy()
    del exchange_rate_dict["target_currency"]["_sa_instance_state"]
    del exchange_rate_dict["target_currency_id"]

    exchange_rate_dict["rate"] = round(float(exchange_rate_dict["rate"]), 2)

    return exchange_rate_dict
