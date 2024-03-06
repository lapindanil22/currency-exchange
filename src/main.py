from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from currencies.models import CurrencyORM
from currencies.router import get_currencies, router as router_currencies
from currencies.schemas import CurrencyWithID
from database import async_session_maker, create_all_tables, drop_all_tables
from exchange.router import router as router_exchange
from exchange_rates.models import ExchangeRateORM
from exchange_rates.router import get_exchange_rates, router as router_exchange_rates
from exchange_rates.schemas import ExchangeRateWithCurrencies, ExchangeRateWithID


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Currency Exchange", lifespan=lifespan)

app.include_router(router_currencies)
app.include_router(router_exchange_rates)
app.include_router(router_exchange)

app.mount("/static", StaticFiles(directory="../static"), name="static")
templates = Jinja2Templates(directory="../templates")

origins = ["http://localhost"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def main(request: Request,
               currencies: Annotated[list[CurrencyWithID], Depends(get_currencies)],
               exchange_rates: Annotated[list[ExchangeRateWithCurrencies], Depends(get_exchange_rates)]):
    return templates.TemplateResponse(
        "index.html", {"request": request, "currencies": currencies, "exchangeRates": exchange_rates}
    )


async def init_db():
    await drop_all_tables()
    await create_all_tables()

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

    async with async_session_maker() as session:
        for currency in currencies:
            session.add(CurrencyORM(**currency))

        for exchange_rate in exchange_rates:
            session.add(ExchangeRateORM(**exchange_rate))

        await session.flush()
        await session.commit()
