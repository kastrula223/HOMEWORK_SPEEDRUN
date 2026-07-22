from flask import Flask, render_template, request

app = Flask(__name__)

app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {"txt", "csv", "log", "md", "json"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/", methods=["GET", "POST"])
def index():
    content = None
    error = None
    filename = None

    if request.method == "POST":
        file = request.files.get("file")

        if file is None or file.filename == "":
            error = "Файл не обрано."
        elif not allowed_file(file.filename):
            error = f"Непідтримуваний тип файлу. Дозволено: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        else:
            try:
                raw_bytes = file.read()
                content = raw_bytes.decode("utf-8")
                filename = file.filename
            except UnicodeDecodeError:
                error = "Не вдалося прочитати файл — переконайтесь, що це текстовий файл у кодуванні UTF-8."

    return render_template("index.html", content=content, error=error, filename=filename)


if __name__ == "__main__":
    app.run(debug=True)