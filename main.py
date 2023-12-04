import json
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer

hostName = "localhost"
serverPort = 8080


def exchange_rates_tuple_to_list_of_dicts(exchange_rates):
    exchange_rates_list = []
    for exchange_rate in exchange_rates:
        base_currency_tuple = cursor.execute("SELECT * FROM currency WHERE id = ?",
                                             (exchange_rate[1],)).fetchone()
        base_currency_json = currencies_tuple_to_list_of_dicts([base_currency_tuple])
        target_currency_tuple = cursor.execute("SELECT * FROM currency WHERE id = ?",
                                               (exchange_rate[2],)).fetchone()
        target_currency_json = currencies_tuple_to_list_of_dicts([target_currency_tuple])

        exchange_rate_dict = {
            "id": exchange_rate[0],
            "baseCurrency": base_currency_json[0],
            "targetCurrency": target_currency_json[0],
            "rate": exchange_rate[3],
        }
        exchange_rates_list.append(exchange_rate_dict)
    return exchange_rates_list


def currencies_tuple_to_list_of_dicts(currencies):
    currencies_dict = []
    for currency in currencies:
        currency_dict = {
            "id": currency[0],
            "code": currency[1],
            "fullName": currency[2],
            "sign": currency[3],
        }
        currencies_dict.append(currency_dict)
    return currencies_dict


class MyServer(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/api/currencies':
            self.get_currencies()
        elif self.path == '/api/exchangeRates':
            self.get_exchange_rates()
        elif re.search("/api/currency/.+", self.path):
            currency = self.path.split("/")[-1]
            self.get_currency(currency)
        else:
            self.send_response(400)
            self.end_headers()

    def get_exchange_rates(self):
        cursor.execute("SELECT * FROM exchange_rate")
        exchange_rates = cursor.fetchall()
        exchange_rates_list_of_dicts = exchange_rates_tuple_to_list_of_dicts(exchange_rates)

        self.send_200_json_headers()
        self.wfile.write(bytes(json.dumps(exchange_rates_list_of_dicts, indent=2), "utf-8"))

    def send_200_json_headers(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def get_currencies(self):
        cursor.execute("SELECT * FROM currency")
        currencies = cursor.fetchall()
        currencies_list_of_dicts = currencies_tuple_to_list_of_dicts(currencies)

        self.send_200_json_headers()
        self.wfile.write(bytes(json.dumps(currencies_list_of_dicts, indent=2), "utf-8"))

    def get_currency(self, currency_code):
        cursor.execute("SELECT * FROM currency WHERE code = ?", (currency_code,))
        currency = cursor.fetchone()
        currency_list_of_dict = currencies_tuple_to_list_of_dicts([currency])

        self.send_200_json_headers()
        self.wfile.write(bytes(json.dumps(currency_list_of_dict, indent=2), "utf-8"))


def init_database_if_not_exists():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "currency" (
            "id"    INTEGER,
            "code"	TEXT,
            "full_name"	TEXT,
            "sign"	TEXT,
            PRIMARY KEY("id")
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS "exchange_rate" (
            "id"	INTEGER,
            "base_currency_id"	INTEGER,
            "target_currency_id"	INTEGER,
            "rate"	NUMERIC,
            FOREIGN KEY("base_currency_id") REFERENCES "currency"("id"),
            FOREIGN KEY("target_currency_id") REFERENCES "currency"("id"),
            PRIMARY KEY("id")
        )
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS "idx_code" ON "currency" (
            "code"
        )
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS "idx_currency_pair" ON "exchange_rate" (
            "base_currency_id",
            "target_currency_id"
        )
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS "idx_id" ON "currency" (
            "id"
        )
    """)


if __name__ == "__main__":
    connection = sqlite3.connect("exchange.sqlite")
    cursor = connection.cursor()
    init_database_if_not_exists()

    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    connection.close()
    webServer.server_close()
    print("Server stopped")
