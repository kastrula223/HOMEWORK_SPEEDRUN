from flask import Flask, url_for

app = Flask(__name__)


@app.route('/')
def home():
    return f'''
        <h1>Ласкаво просимо до світу подорожей!</h1>
        <p>Обирайте найкращі маршрути разом із нами.</p>
        <nav>
            <a href="{url_for('countries')}"><button>Країни</button></a>
            <a href="{url_for('contact')}"><button>Контакти</button></a>
        </nav>
    '''


@app.route('/countries')
def countries():
    return f'''
        <h1>Топ-5 місць для подорожей</h1>
        <ul>
            <li>Ісландія — Країна гейзерів та вулканів</li>
            <li>Японія — Цвітіння сакури та футуризм</li>
            <li>Італія — Історія, культура та гастрономія</li>
            <li>Норвегія — Величні фіорди</li>
            <li>Єгипет — Загадкові піраміди</li>
        </ul>
        <nav>
            <a href="{url_for('home')}"><button>Головна</button></a>
            <a href="{url_for('contact')}"><button>Контакти</button></a>
        </nav>
    '''


@app.route('/contact/')
def contact():
    return f'''
        <h1>Зв’язок з турагентом</h1>
        <p>Залиште заявку, і ми зв'яжемося з вами!</p>
        <form>
            <label>Ім'я: <input type="text" name="name"></label><br><br>
            <label>Повідомлення: <textarea name="message"></textarea></label><br><br>
            <button type="submit">Надіслати</button>
        </form>
        <br>
        <nav>
            <a href="{url_for('home')}"><button>Головна</button></a>
            <a href="{url_for('countries')}"><button>Країни</button></a>
        </nav>
    '''


if __name__ == '__main__':
    app.run(debug=True)