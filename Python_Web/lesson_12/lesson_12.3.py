from flask import Flask, redirect, request, url_for

app = Flask(__name__)

participants_list = []


@app.route("/")
def home():
    return redirect("/event_register")


@app.route('/event_register', methods=['GET', 'POST'])
def register():
    error = None

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        time_slot = request.form.get('time_slot', '').strip()

        if not name or not email or not time_slot:
            error = "Будь ласка, заповніть усі поля!"
        else:
            participants_list.append(
                {'name': name, 'email': email, 'time_slot': time_slot}
            )
            return redirect(url_for('participants'))

    error_alert = (
        f'<div class="alert alert-danger">{error}</div>' if error else ''
    )

    return f'''
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>Реєстрація на вебінар</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container py-5" style="max-width: 500px;">
            <div class="card shadow-sm p-4">
                <h2 class="mb-4 text-center">Реєстрація на онлайн-лекцію</h2>
                {error_alert}
                <form method="POST">
                    <div class="mb-3">
                        <label class="form-label">Ім'я:</label>
                        <input type="text" name="name" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Email:</label>
                        <input type="email" name="email" class="form-control">
                    </div>
                    <div class="mb-3">
                        <label class="form-label">Бажаний час участі:</label>
                        <select name="time_slot" class="form-select">
                            <option value="">Оберіть час...</option>
                            <option value="Ранок (09:00)">Ранок (09:00)</option>
                            <option value="День (14:00)">День (14:00)</option>
                            <option value="Вечір (19:00)">Вечір (19:00)</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Зареєструватися</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    '''


@app.route('/participants')
def participants():
    rows = ''
    for p in participants_list:
        rows += f'<tr><td>{p["name"]}</td><td>{p["email"]}</td><td>{p["time_slot"]}</td></tr>'

    return f'''
    <!DOCTYPE html>
    <html lang="uk">
    <head>
        <meta charset="UTF-8">
        <title>Список учасників</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body class="bg-light">
        <div class="container py-5" style="max-width: 700px;">
            <h2 class="mb-4 text-center">Зареєстровані учасники</h2>
            <div class="table-responsive">
                <table class="table table-striped table-hover bg-white rounded shadow-sm">
                    <thead class="table-primary">
                        <tr>
                            <th>Ім'я</th>
                            <th>Email</th>
                            <th>Обраний час</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows if rows else '<tr><td colspan="3" class="text-center">Поки немає зареєстрованих учасників</td></tr>'}
                    </tbody>
                </table>
            </div>
            <a href="{url_for('register')}" class="btn btn-secondary">← Зареєструвати ще одного</a>
        </div>
    </body>
    </html>
    '''


if __name__ == '__main__':
    app.run(debug=True)