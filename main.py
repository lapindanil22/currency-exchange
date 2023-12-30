import json
import re
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse

hostName = "localhost"  # Or "0.0.0.0" to be able to see server in whole LAN
serverPort = 8080


def exchange_rates_tuple_to_list_of_dicts(exchange_rates):
    exchange_rates_list = []
    for exchange_rate in exchange_rates:
        base_currency_tuple = cursor.execute(
            "SELECT * FROM currency WHERE id = ?", (exchange_rate[1],)).fetchone()
        base_currency_json = currencies_tuple_to_list_of_dicts([base_currency_tuple])
        target_currency_tuple = cursor.execute(
            "SELECT * FROM currency WHERE id = ?", (exchange_rate[2],)).fetchone()
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
        if self.path == "/api/currencies":
            self.get_currencies()
        elif self.path == "/api/exchangeRates":
            self.get_exchange_rates()
        elif re.search("/api/exchangeRate/.+", self.path):
            currency_pair = self.path.split("/")[-1]
            base_currency = currency_pair[:3]
            target_currency = currency_pair[3:]
            self.get_exchange_rate(base_currency, target_currency)
        elif re.search("/api/exchange\?.+", self.path):
            query_dict = dict(parse.parse_qsl(parse.urlsplit(self.path).query))
            self.get_exchange(query_dict["from"], query_dict["to"], query_dict["amount"])
        elif re.search("/api/currency/.+", self.path):
            currency = self.path.split("/")[-1]
            self.get_currency(currency)
        else:
            self.send_response(400)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/currencies":
            # self.post_currency()
            self.send_response(400)
        else:
            self.send_response(400)
            self.end_headers()

    def get_exchange(self, from_currency, to_currency, amount):
        cursor.execute("""
            SELECT er.*
            FROM exchange_rate AS er
            JOIN currency AS c1 ON er.base_currency_id = c1.id
            JOIN currency AS c2 ON er.target_currency_id = c2.id
            WHERE c1.code = ? AND c2.code = ?
        """, (from_currency, to_currency))
        exchange_rate = cursor.fetchone()
        exchange_rate_dict = exchange_rates_tuple_to_list_of_dicts([exchange_rate])[0]
        exchange_rate_dict["amount"] = amount
        exchange_rate_dict["convertedAmount"] = round(float(exchange_rate_dict["rate"]) *
                                                      float(amount), 2)

        self.send_200_json_headers()
        self.wfile.write(bytes(json.dumps(exchange_rate_dict, indent=2), "utf-8"))

    def get_exchange_rate(self, base_currency, target_currency):
        cursor.execute("""
            SELECT er.*
            FROM exchange_rate AS er
            JOIN currency AS c1 ON er.base_currency_id = c1.id
            JOIN currency AS c2 ON er.target_currency_id = c2.id
            WHERE c1.code = ? AND c2.code = ?
        """, (base_currency, target_currency))
        exchange_rate = cursor.fetchone()
        exchange_rate_dict = exchange_rates_tuple_to_list_of_dicts([exchange_rate])[0]

        self.send_200_json_headers()
        self.wfile.write(bytes(json.dumps(exchange_rate_dict, indent=2), "utf-8"))

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
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS currency (
            id INTEGER PRIMARY KEY,
            code TEXT,
            full_name TEXT,
            sign TEXT
        );

        CREATE TABLE IF NOT EXISTS exchange_rate (
            id INTEGER PRIMARY KEY,
            base_currency_id INTEGER REFERENCES currency(id),
            target_currency_id INTEGER REFERENCES currency(id),
            rate NUMERIC
        );

        CREATE UNIQUE INDEX IF NOT EXISTS idx_code ON currency(code);

        CREATE UNIQUE INDEX IF NOT EXISTS idx_currency_pair ON exchange_rate (
            base_currency_id,
            target_currency_id
        );

        CREATE INDEX IF NOT EXISTS idx_id ON currency(id);
    """)


if __name__ == "__main__":
    connection = sqlite3.connect("exchange.sqlite")
    cursor = connection.cursor()
    init_database_if_not_exists()

    webServer = HTTPServer((hostName, serverPort), MyServer)
    print(f"Server started http://{hostName}:{serverPort}")

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    connection.close()
    webServer.server_close()
    print("Server stopped")
