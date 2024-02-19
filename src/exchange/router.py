from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, aliased

from currencies.models import CurrencyModel
from database import get_db
from exchange_rates.models import ExchangeRateModel

router = APIRouter(
    prefix="/exchange",
    tags=["Exchange"]
)


@router.get("")
def get_exchange(baseCode: Annotated[str, Query()],
                 targetCode: Annotated[str, Query()],
                 amount: Annotated[float, Query()],
                 db: Session = Depends(get_db)):
    base_currency = db.query(CurrencyModel).filter(CurrencyModel.code == baseCode).first()
    target_currency = db.query(CurrencyModel).filter(CurrencyModel.code == targetCode).first()
    if not base_currency or not target_currency:
        return JSONResponse(
            status_code=404,
            content={"message": "Одна (или обе) валюта из валютной пары не существует в БД"}
        )

    c1 = aliased(CurrencyModel)
    c2 = aliased(CurrencyModel)
    exchange_rate = db.query(ExchangeRateModel) \
        .join(c1, ExchangeRateModel.base_currency_id == c1.id) \
        .join(c2, ExchangeRateModel.target_currency_id == c2.id) \
        .filter(c1.code == baseCode, c2.code == targetCode).first()

    if not exchange_rate:
        return JSONResponse(
            status_code=404,
            content={"message": "Обменный курс для пары не найден"}
        )

    base_currency = db.query(CurrencyModel).filter(CurrencyModel.code == baseCode).first()
    target_currency = db.query(CurrencyModel).filter(CurrencyModel.code == targetCode).first()

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
