import requests


def test_get_currencies():
    response = requests.get("http://localhost:8000/currencies")
    assert response.status_code == 200


def test_get_currency():
    response = requests.get("http://localhost:8000/currencies/USD")
    assert response.status_code == 200
    response = requests.get("http://localhost:8000/currencies/LOL")
    assert response.status_code == 404


def test_get_exchange_rates():
    response = requests.get("http://localhost:8000/exchangeRates")
    assert response.status_code == 200


def test_get_exchange_rate():
    response = requests.get("http://localhost:8000/exchangeRates/USDRUB")
    assert response.status_code == 200
    response = requests.get("http://localhost:8000/exchangeRates/LOLKEK")
    assert response.status_code == 404


def test_get_exchange():
    response = requests.get("http://localhost:8000/exchange?baseCode=USD&targetCode=RUB&amount=10")
    assert response.status_code == 200
    response = requests.get("http://localhost:8000/exchange?baseCode=KZT&targetCode=JPY&amount=10")
    assert response.status_code == 404
    response = requests.get("http://localhost:8000/exchange?baseCode=LOL&targetCode=KEK&amount=10")
    assert response.status_code == 404
