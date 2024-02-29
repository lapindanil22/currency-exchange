import requests


def test_create_currency():
    data_1 = {
        "code": "LOL",
        "name": "Laugh Out Loud",
        "sign": "L"
    }
    data_2 = {
        "code": "KEK",
        "name": "Keck Observatory",
        "sign": "K"
    }

    response = requests.post("http://localhost:8000/currencies", json=data_1)
    assert response.status_code == 200
    assert response.json()["code"] == "LOL"

    response = requests.post("http://localhost:8000/currencies", json=data_2)
    assert response.status_code == 200
    assert response.json()["code"] == "KEK"

    response = requests.post("http://localhost:8000/currencies", json=data_2)
    assert response.status_code == 409


def test_create_exchange_rate():
    data_valid = {
        "rate": 12.34,
        "baseCurrencyCode": "LOL",
        "targetCurrencyCode": "KEK"
    }
    data_invalid = {
        "rate": 12.34,
        "baseCurrencyCode": "NNN",
        "targetCurrencyCode": "ZZZ"
    }

    response = requests.post("http://localhost:8000/exchangeRates", json=data_valid)
    assert response.status_code == 200
    assert response.json()["rate"] == 12.34

    response = requests.post("http://localhost:8000/exchangeRates", json=data_valid)
    assert response.status_code == 409

    response = requests.post("http://localhost:8000/exchangeRates", json=data_invalid)
    assert response.status_code == 404


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

    # For existing currencies
    response = requests.get("http://localhost:8000/exchangeRates/KEKLOL")
    assert response.status_code == 404

    # For non-existent currency / currencies
    response = requests.get("http://localhost:8000/exchangeRates/NNNZZZ")
    assert response.status_code == 404


def test_get_exchange():
    response = requests.get(
        "http://localhost:8000/exchange?baseCode=LOL&targetCode=KEK&amount=43.21"
    )
    assert response.status_code == 200
    assert response.json()["converted_amount"] == round(12.34 * 43.21, 2)

    # For existing currencies
    response = requests.get(
        "http://localhost:8000/exchange?baseCode=KEK&targetCode=LOL&amount=43.21"
    )
    assert response.status_code == 404

    # For non-existent currency / currencies
    response = requests.get(
        "http://localhost:8000/exchange?baseCode=NNN&targetCode=ZZZ&amount=43.21"
    )
    assert response.status_code == 404


def test_patch_exchange_rate():
    response = requests.patch("http://localhost:8000/exchangeRates/LOLKEK",
                              data=str(23.45).encode())
    assert response.status_code == 200
    assert response.json()["rate"] == 23.45

    # For existing currencies
    response = requests.patch("http://localhost:8000/exchangeRates/KEKLOL",
                              data=str(23.45).encode())
    assert response.status_code == 404

    # For non-existent currency / currencies
    response = requests.patch("http://localhost:8000/exchangeRates/NNNZZZ",
                              data=str(23.45).encode())
    assert response.status_code == 404


def test_delete_exchange_rate():
    response = requests.delete("http://localhost:8000/exchangeRates/LOLKEK")
    assert response.status_code == 200
    assert response.json()["rate"] == 23.45

    # For existing currencies
    response = requests.delete("http://localhost:8000/exchangeRates/LOLKEK")
    assert response.status_code == 404

    # For non-existent currency / currencies
    response = requests.delete("http://localhost:8000/exchangeRates/NNNZZZ")
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
