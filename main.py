from database import Base, Currency, ExchangeRate, engine, SessionLocal
from sqlalchemy.orm import Session
from fastapi import Body, FastAPI, Depends
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


@app.post("/api/currencies/")
def post_currency(data=Body(), db: Session = Depends(get_db)):
    currency = Currency(name=data["name"], code=data["code"], sign=data["sign"])
    db.add(currency)
    db.commit()
    db.refresh(currency)
    return currency


@app.get("/api/exchangeRates")
def get_exchange_rates(db: Session = Depends(get_db)):
    return db.query(ExchangeRate).all()


@app.get("/api/exchangeRates/{exchange_pair}")
def get_exchange_rate(exchange_pair, db: Session = Depends(get_db)):
    exchange_rate = db.query(ExchangeRate).filter(...).first()
    if not exchange_rate:
        return JSONResponse(status_code=404,
                            content={"message": "Обменный курс для пары не найден"})
    return exchange_rate


@app.post("/api/exchangeRates/")
def post_exchange_rate(data=Body(), db: Session = Depends(get_db)):
    exchange_rate = ExchangeRate(base_currency_code=data["base_currency_code"],
                                 target_currency_code=data["target_currency_code"],
                                 rate=data["rate"])
    db.add(exchange_rate)
    db.commit()
    db.refresh(exchange_rate)
    return exchange_rate


@app.patch("/api/exchangeRates/{pair}")
def patch_exchange_rate(data=Body(), db: Session = Depends(get_db)):
    exchange_rate = db.query(ExchangeRate).filter(...).first()
    if not exchange_rate:
        return JSONResponse(status_code=404,
                            content={"message": "Обменный курс для пары не найден"})
    exchange_rate.rate = data["rate"]
    db.commit()
    db.refresh(exchange_rate)
    return exchange_rate


# /exchange?from=BASE_CURRENCY_CODE&to=TARGET_CURRENCY_CODE&amount=$AMOUNT
@app.get("/exchange")
def get_exchange(db: Session = Depends(get_db)):
    pass
