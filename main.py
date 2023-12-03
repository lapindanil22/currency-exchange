import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = "localhost"
serverPort = 8080


def exchange_rates_list_to_json(exchange_rates):
    exchange_rates_list = []
    for exchange_rate in exchange_rates:
        base_currency_tuple = cursor.execute("SELECT * FROM currency WHERE id = ?",
                                             (exchange_rate[1],)).fetchone()
        base_currency_json = currencies_list_to_json([base_currency_tuple])
        target_currency_tuple = cursor.execute("SELECT * FROM currency WHERE id = ?",
                                               (exchange_rate[2],)).fetchone()
        target_currency_json = currencies_list_to_json([target_currency_tuple])

        exchange_rate_dict = {
            "id": exchange_rate[0],
            "baseCurrency": base_currency_json[0],
            "targetCurrency": target_currency_json[0],
            "rate": exchange_rate[3],
        }
        exchange_rates_list.append(exchange_rate_dict)
    return exchange_rates_list


def currencies_list_to_json(currencies):
    currencies_list = []
    for currency in currencies:
        currency_dict = {
            "id": currency[0],
            "code": currency[1],
            "fullName": currency[2],
            "sign": currency[3],
        }
        currencies_list.append(currency_dict)
    return currencies_list


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/currencies':
            self.get_currencies()
        elif self.path == '/api/exchangeRates':
            self.get_exchange_rates()
        else:
            self.send_response(400)
            self.end_headers()

    def get_exchange_rates(self):
        cursor.execute("SELECT * FROM exchange_rate")
        exchange_rates = cursor.fetchall()
        exchange_rates_list = exchange_rates_list_to_json(exchange_rates)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(exchange_rates_list, indent=2), "utf-8"))

    def get_currencies(self):
        cursor.execute("SELECT * FROM currency")
        currencies = cursor.fetchall()
        currencies_list = currencies_list_to_json(currencies)

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(currencies_list, indent=2), "utf-8"))


if __name__ == "__main__":
    connection = sqlite3.connect("exchange.sqlite")
    cursor = connection.cursor()
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    connection.close()
    webServer.server_close()
    print("Server stopped")
