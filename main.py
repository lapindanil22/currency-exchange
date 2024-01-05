from typing import Annotated
from database import Base, Currency, ExchangeRate, engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi import Body, FastAPI, Depends, Form
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


@app.get("/api/currencies/{code}")
def get_currency(code, db: Session = Depends(get_db)):
    currency = db.query(Currency).filter(Currency.code == code).first()
    if not currency:
        return JSONResponse(status_code=404, content={"message": "Валюта не найдена"})
    return currency


@app.post("/api/currencies")
def post_currency(name: Annotated[str, Form()],
                  code: Annotated[str, Form()],
                  sign: Annotated[str, Form()],
                  db: Session = Depends(get_db)):
    currency = Currency(name=name, code=code, sign=sign)
    db.add(currency)
    db.commit()
    db.refresh(currency)
    return currency


@app.get("/api/exchangeRates")
def get_exchange_rates(db: Session = Depends(get_db)):
    return db.query(ExchangeRate).all()


@app.get("/api/exchangeRate/{exchange_pair}")
def get_exchange_rate(exchange_pair, db: Session = Depends(get_db)):
    base_currency_code = exchange_pair[:3]
    target_currency_code = exchange_pair[3:]

    exchange_rate = db.query(ExchangeRate).filter().first()
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


@app.patch("/api/exchangeRate/{pair}")
def patch_exchange_rate(data=Body(), db: Session = Depends(get_db)):
    exchange_rate = db.query(ExchangeRate).filter(...).first()
    if not exchange_rate:
        return JSONResponse(status_code=404,
                            content={"message": "Обменный курс для пары не найден"})
    exchange_rate.rate = data["rate"]
    db.commit()
    db.refresh(exchange_rate)
    return exchange_rate


@app.get("/api/exchange")
def get_exchange(baseCode: str, targetCode: str, amount: float, db: Session = Depends(get_db)):
    return JSONResponse({"fromCode": baseCode, "toCode": targetCode, "amount": amount})
