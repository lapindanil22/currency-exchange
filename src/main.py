from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from currencies.models import CurrencyORM
from currencies.router import router as router_currencies
from database import Base, db, engine
from exchange.router import router as router_exchange
from exchange_rates.models import ExchangeRateORM
from exchange_rates.router import router as router_exchange_rates


@asynccontextmanager
async def lifespan(app: FastAPI):
    # init_db()
    # print("База очищена")
    # print("База готова к работе")
    yield
    print("Выключение")


app = FastAPI(
    title="Currency Exchange",
    lifespan=lifespan
)

app.include_router(router_currencies)
app.include_router(router_exchange_rates)
app.include_router(router_exchange)

app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates")

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
def main(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    currencies = [
        {"name": "US Dollar", "code": "USD", "sign": "$"},
        {"name": "Russian Ruble", "code": "RUB", "sign": "₽"},
        {"name": "Euro", "code": "EUR", "sign": "€"},
        {"name": "Kazakhstani Tenge", "code": "KZT", "sign": "₸"},
        {"name": "Japanese yen", "code": "JPY", "sign": "¥"},
    ]

    exchange_rates = [
        {"base_currency_id": 1, "target_currency_id": 2, "rate": 92.35},
        {"base_currency_id": 3, "target_currency_id": 2, "rate": 100.3},
        {"base_currency_id": 4, "target_currency_id": 2, "rate": 0.19},
        {"base_currency_id": 5, "target_currency_id": 2, "rate": 0.61},
        {"base_currency_id": 1, "target_currency_id": 3, "rate": 0.91},
    ]

    for currency in currencies:
        db.add(CurrencyORM(**currency))

    for exchange_rate in exchange_rates:
        db.add(ExchangeRateORM(**exchange_rate))

    db.commit()
    db.close()
