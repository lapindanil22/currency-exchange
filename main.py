from typing import Annotated
from database import Base, Currency, ExchangeRate, engine, SessionLocal
from sqlalchemy.orm import Session, aliased
from fastapi import FastAPI, Depends, Form, Path, Query
from fastapi.responses import JSONResponse


Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/currencies")
def get_currencies(db: Session = Depends(get_db)):
    return db.query(Currency).all()


@app.get("/api/currency/{code}")
def get_currency_empty(code: Annotated[str, Path()],
                       db: Session = Depends(get_db)):
    currency = db.query(Currency).filter(Currency.code == code).first()
    if not currency:
        return JSONResponse(status_code=404, content={"message": "Валюта не найдена"})
    return currency


@app.post("/api/currencies")
def post_currency(name: Annotated[str, Form()],
                  code: Annotated[str, Form()],
                  sign: Annotated[str, Form()],
                  db: Session = Depends(get_db)):
    if db.query(Currency).filter(Currency.code == code).first():
        return JSONResponse(status_code=409,
                            content={"message": "Валюта с таким кодом уже существует"})
    currency = Currency(name=name, code=code, sign=sign)
    db.add(currency)
    db.commit()
    db.refresh(currency)
    return currency


@app.get("/api/exchangeRates")
def get_exchange_rates(db: Session = Depends(get_db)):
    return db.query(ExchangeRate).all()


@app.get("/api/exchangeRate/{exchange_pair}")
def get_exchange_rate(exchange_pair: Annotated[str, Path()],
                      db: Session = Depends(get_db)):
    base_currency_code = exchange_pair[:3]
    target_currency_code = exchange_pair[3:]

    c1 = aliased(Currency)
    c2 = aliased(Currency)
    exchange_rate = db.query(ExchangeRate) \
        .join(c1, ExchangeRate.base_currency_id == c1.id) \
        .join(c2, ExchangeRate.target_currency_id == c2.id) \
        .filter(c1.code == base_currency_code, c2.code == target_currency_code).first()

    if not exchange_rate:
        return JSONResponse(status_code=404,
                            content={"message": "Обменный курс для пары не найден"})
    return exchange_rate


@app.post("/api/exchangeRates")
def post_exchange_rate(baseCurrencyCode: Annotated[str, Form()],
                       targetCurrencyCode: Annotated[str, Form()],
                       rate: Annotated[float, Form()],
                       db: Session = Depends(get_db)):
    base_currency = db.query(Currency).filter(Currency.code == baseCurrencyCode).first()
    target_currency = db.query(Currency).filter(Currency.code == targetCurrencyCode).first()
    if not base_currency or not target_currency:
        return JSONResponse(status_code=404,
                            content={"message": "Одна (или обе) валюта из валютной пары не существует в БД"})

    if db.query(ExchangeRate).filter(ExchangeRate.base_currency_id == base_currency.id,
                                     ExchangeRate.target_currency_id == target_currency.id).first():
        return JSONResponse(status_code=409,
                            content={"message": "Валютная пара с таким кодом уже существует"})

    base_currency_json = base_currency.__dict__.copy()
    target_currency_json = target_currency.__dict__.copy()

    exchange_rate = ExchangeRate(base_currency_id=base_currency.id,
                                 target_currency_id=target_currency.id,
                                 rate=rate)
    db.add(exchange_rate)
    db.commit()
    db.refresh(exchange_rate)

    exchange_rate_json = exchange_rate.__dict__.copy()

    exchange_rate_json["rate"] = round(float(exchange_rate_json["rate"]), 2)

    exchange_rate_json.pop("_sa_instance_state")
    base_currency_json.pop("_sa_instance_state")
    target_currency_json.pop("_sa_instance_state")

    exchange_rate_json.pop("base_currency_id")
    exchange_rate_json.pop("target_currency_id")

    exchange_rate_json["base_currency"] = base_currency_json
    exchange_rate_json["target_currency"] = target_currency_json

    return JSONResponse(content=exchange_rate_json)


@app.patch("/api/exchangeRate/{exchange_pair}")
def patch_exchange_rate(exchange_pair: Annotated[str, Path()],
                        rate: Annotated[float, Form()],
                        db: Session = Depends(get_db)):
    base_currency_code = exchange_pair[:3]
    target_currency_code = exchange_pair[3:]

    base_currency = db.query(Currency).filter(Currency.code == base_currency_code).first()
    target_currency = db.query(Currency).filter(Currency.code == target_currency_code).first()
    if not base_currency or not target_currency:
        return JSONResponse(status_code=404,
                            content={"message": "Валютная пара отсутствует в базе данных"})

    c1 = aliased(Currency)
    c2 = aliased(Currency)
    exchange_rate = db.query(ExchangeRate) \
        .join(c1, ExchangeRate.base_currency_id == c1.id) \
        .join(c2, ExchangeRate.target_currency_id == c2.id) \
        .filter(c1.code == base_currency_code, c2.code == target_currency_code).first()

    if not exchange_rate:
        return JSONResponse(status_code=404,
                            content={"message": "Обменный курс для пары не найден"})
    exchange_rate.rate = rate
    db.commit()
    db.refresh(exchange_rate)
    return exchange_rate


@app.get("/api/exchange")
def get_exchange(baseCode: Annotated[str, Query()],
                 targetCode: Annotated[str, Query()],
                 amount: Annotated[float, Query()],
                 db: Session = Depends(get_db)):
    base_currency = db.query(Currency).filter(Currency.code == baseCode).first()
    target_currency = db.query(Currency).filter(Currency.code == targetCode).first()
    if not base_currency or not target_currency:
        return JSONResponse(status_code=404,
                            content={"message": "Одна (или обе) валюта из валютной пары не существует в БД"})

    c1 = aliased(Currency)
    c2 = aliased(Currency)
    exchange_rate = db.query(ExchangeRate) \
        .join(c1, ExchangeRate.base_currency_id == c1.id) \
        .join(c2, ExchangeRate.target_currency_id == c2.id) \
        .filter(c1.code == baseCode, c2.code == targetCode).first()

    if not exchange_rate:
        return JSONResponse(status_code=404,
                            content={"message": "Обменный курс для пары не найден"})

    base_currency = db.query(Currency).filter(Currency.code == baseCode).first()
    target_currency = db.query(Currency).filter(Currency.code == targetCode).first()

    base_currency_json = base_currency.__dict__.copy()
    target_currency_json = target_currency.__dict__.copy()

    exchange_json = {
        "base_currency": base_currency_json,
        "target_currency": target_currency_json,
        "rate": exchange_rate.rate,
        "amount": amount,
        "converted_amount": round(float(exchange_rate.rate) * amount, 2)
    }

    return exchange_json
