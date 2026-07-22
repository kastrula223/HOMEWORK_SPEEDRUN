from flask import Flask, jsonify
import requests

app = Flask(__name__)

API = "https://api.coingecko.com/api/v3/simple/price"
#Кароче https://api.coindesk.com/v1/bpi/currentprice.json ЗДОХ нафіг тому я використав альтернативу

def format_price(value: float) -> str:
    return f"{value:,.2f}"


@app.route("/crypto", methods=["GET"])
def get_crypto_price():
    params = {
        "ids": "bitcoin",
        "vs_currencies": "usd,eur,gbp",
    }
    try:
        response = requests.get(API, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        bitcoin = data["bitcoin"]
        result = {
            "USD": format_price(bitcoin["usd"]),
            "EUR": format_price(bitcoin["eur"]),
            "GBP": format_price(bitcoin["gbp"]),
        }
        return jsonify(result), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Не вдалося отримати дані з CoinGecko API", "details": str(e)}), 502
    except (KeyError, ValueError) as e:
        return jsonify({"error": "Некоректна структура відповіді від API", "details": str(e)}), 502


if __name__ == "__main__":
    app.run(debug=True, port=5000)