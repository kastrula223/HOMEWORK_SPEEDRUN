from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFError
import secrets

app = Flask(__name__)

app.config["SECRET_KEY"] = secrets.token_hex(32)

csrf = CSRFProtect(app)

users = {}
messages = []


@app.route("/")
def index():
    return render_template("index.html", users=users, messages=messages)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Заповніть усі поля.", "error")
        elif username in users:
            flash("Такий користувач вже існує.", "error")
        else:
            users[username] = password
            flash(f"Користувача '{username}' успішно зареєстровано!", "success")
            return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if users.get(username) == password:
            session["user"] = username
            flash(f"Вітаємо, {username}!", "success")
            return redirect(url_for("index"))
        else:
            flash("Невірний логін або пароль.", "error")

    return render_template("login.html")


@app.route("/message", methods=["GET", "POST"])
def message():
    if request.method == "POST":
        text = request.form.get("text", "").strip()
        author = session.get("user", "Анонім")

        if not text:
            flash("Повідомлення не може бути порожнім.", "error")
        else:
            messages.append({"author": author, "text": text})
            flash("Повідомлення надіслано!", "success")
            return redirect(url_for("index"))

    return render_template("message.html")


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template("csrf_error.html", reason=e.description), 400


if __name__ == "__main__":
    app.run(debug=True, port=5003)