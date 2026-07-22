import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)


@app.route('/user', methods=['POST'])
def user():
    data = request.get_json(silent=True) or {}

    if "username" not in data or not data["username"]:
        app.logger.warning("User registration/login attempt without username!")
        return jsonify({"error": "Username is required"}), 400

    username = data["username"]
    app.logger.info(f"User '{username}' successfully greeted.")
    return jsonify({"message": f"Hello, {username}!"}), 200


if __name__ == '__main__':
    app.run(debug=True)