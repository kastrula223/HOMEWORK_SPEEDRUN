import random
from flask import Flask, abort, redirect, url_for

app = Flask(__name__)

MOVIES = {
    1: {
        "title": "Інтерстеллар",
        "description": "Подорож групи дослідників через червоточину в просторі.",
    },
    2: {
        "title": "Початок",
        "description": "Злодій, який викрадає корпоративні таємниці через використання технології обміну снами.",
    },
    3: {
        "title": "Матриця",
        "description": "Комп'ютерний хакер дізнається про справжню природу своєї реальності.",
    },
}


@app.route('/')
def index():
    html = '<h1>Популярні фільми</h1><ul>'
    for movie_id, movie in MOVIES.items():
        html += f'<li><a href="{url_for("movie_detail", id=movie_id)}">{movie["title"]}</a></li>'
    html += f'</ul><p><a href="{url_for("random_movie")}">Переглянути випадковий фільм</a></p>'
    return html


@app.route('/movie/<int:id>')
def movie_detail(id):
    movie = MOVIES.get(id)
    if not movie:
        abort(404)

    return f'''
        <h1>{movie["title"]}</h1>
        <p>{movie["description"]}</p>
        <a href="{url_for('index')}">← Назад до списку</a>
    '''


@app.route('/random')
def random_movie():
    random_id = random.choice(list(MOVIES.keys()))
    return redirect(url_for('movie_detail', id=random_id))


if __name__ == '__main__':
    app.run(debug=True)