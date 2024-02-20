import requests


def test_get_currencies():
    response = requests.get("http://localhost:8000/currencies")
    assert response.status_code == 200


def test_get_currency():
    response = requests.get("http://localhost:8000/currencies/USD")
    assert response.status_code == 200


def test_get_exchange_rates():
    response = requests.get("http://localhost:8000/exchangeRates")
    assert response.status_code == 200


def test_get_exchange_rate():
    response = requests.get("http://localhost:8000/exchangeRates/USDRUB")
    assert response.status_code == 200


def test_get_exchange():
    response = requests.get("http://localhost:8000/exchange?baseCode=USD&targetCode=RUB&amount=10")
    assert response.status_code == 200
