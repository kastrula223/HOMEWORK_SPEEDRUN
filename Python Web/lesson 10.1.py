from flask import Flask

app = Flask(__name__)


@app.route('/')
def home():
    return '<h1>Головна сторінка</h1><p>Ласкаво просимо на наш сайт!</p>'


@app.route('/about/')
def about():
    return '<h1>Про нас</h1><p>Ми компанія, яка розробляє сучасні веб-рішення.</p>'


@app.route('/services/')
def services():
    return (
        '<h1>Наші послуги</h1>'
        '<ul>'
        '<li>Веб-розробка</li>'
        '<li>Дизайн та UI/UX</li>'
        '<li>Консалтинг</li>'
        '</ul>'
    )


@app.route('/contact/')
def contact():
    return (
        '<h1>Контакти</h1>'
        '<p>Email: info@example.com</p>'
        '<p>Телефон: +380 44 123 45 67</p>'
    )


if __name__ == '__main__':
    app.run(debug=True)