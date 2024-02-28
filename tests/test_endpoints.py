import requests


def test_create_currency():
    response = requests.post(
        "http://localhost:8000/currencies",
        json={
            "code": "LOL",
            "name": "Laugh Out Loud",
            "sign": "L"
        }
    )
    assert response.status_code == 200
    assert response.json()["code"] == "LOL"

    response = requests.post(
        "http://localhost:8000/currencies",
        json={
            "code": "KEK",
            "name": "Keck Observatory",
            "sign": "K"
        }
    )
    assert response.status_code == 200
    assert response.json()["code"] == "KEK"


def test_create_exchange_rate():
    response = requests.post(
        "http://localhost:8000/exchangeRates",
        json={
            "rate": 12.34,
            "baseCurrencyCode": "LOL",
            "targetCurrencyCode": "KEK"
        }
    )
    assert response.status_code == 200
    assert response.json()["rate"] == 12.34


def test_get_currencies():
    response = requests.get("http://localhost:8000/currencies")
    assert response.status_code == 200


def test_get_currency():
    response = requests.get("http://localhost:8000/currencies/LOL")
    assert response.status_code == 200
    assert response.json()["code"] == "LOL"

    response = requests.get("http://localhost:8000/currencies/NNN")
    assert response.status_code == 404


def test_get_exchange_rates():
    response = requests.get("http://localhost:8000/exchangeRates")
    assert response.status_code == 200


def test_get_exchange_rate():
    response = requests.get("http://localhost:8000/exchangeRates/LOLKEK")
    assert response.status_code == 200
    assert response.json()["rate"] == 12.34

    response = requests.get("http://localhost:8000/exchangeRates/KEKLOL")
    assert response.status_code == 404

    response = requests.get("http://localhost:8000/exchangeRates/NNNZZZ")
    assert response.status_code == 404


def test_get_exchange():
    response = requests.get(
        "http://localhost:8000/exchange?baseCode=LOL&targetCode=KEK&amount=43.21"
    )
    assert response.status_code == 200
    assert response.json()["converted_amount"] == round(12.34 * 43.21, 2)

    response = requests.get(
        "http://localhost:8000/exchange?baseCode=KEK&targetCode=LOL&amount=43.21"
    )
    assert response.status_code == 404

    response = requests.get(
        "http://localhost:8000/exchange?baseCode=NNN&targetCode=ZZZ&amount=43.21"
    )
    assert response.status_code == 404


def test_patch_exchange_rate():
    response = requests.patch(
        "http://localhost:8000/exchangeRates/LOLKEK",
        data=str(23.45).encode()
    )
    assert response.status_code == 200
    assert response.json()["rate"] == 23.45


def test_delete_exchange_rate():
    response = requests.delete("http://localhost:8000/exchangeRates/LOLKEK")
    assert response.status_code == 200
    assert response.json()["rate"] == 23.45

    response = requests.delete("http://localhost:8000/exchangeRates/LOLKEK")
    assert response.status_code == 404


def test_delete_currency():
    response = requests.delete("http://localhost:8000/currencies/LOL")
    assert response.status_code == 200
    assert response.json()["code"] == "LOL"

    response = requests.delete("http://localhost:8000/currencies/KEK")
    assert response.status_code == 200
    assert response.json()["code"] == "KEK"

    response = requests.delete("http://localhost:8000/currencies/KEK")
    assert response.status_code == 404
