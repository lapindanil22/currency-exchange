from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from src.currencies.router import router as router_currencies
from src.exchange_rates.router import router as router_exchange_rates
from src.exchange.router import router as router_exchange


app = FastAPI(
    title="Currency Exchange"
)

app.include_router(router_currencies)
app.include_router(router_exchange_rates)
app.include_router(router_exchange)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

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
