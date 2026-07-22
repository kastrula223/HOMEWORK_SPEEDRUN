from flask import Flask, render_template, request
import urllib.parse

app = Flask(__name__)

QR_API_URL = "https://api.qrserver.com/v1/create-qr-code/"


@app.route("/", methods=["GET", "POST"])
def index():
    qr_url = None
    text = ""

    if request.method == "POST":
        text = request.form.get("text", "").strip()
        if text:
            encoded_text = urllib.parse.quote(text)
            qr_url = f"{QR_API_URL}?size=150x150&data={encoded_text}"

    return render_template("index.html", qr_url=qr_url, text=text)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
