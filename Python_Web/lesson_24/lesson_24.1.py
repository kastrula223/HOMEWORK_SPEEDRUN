import logging
from flask import Flask, jsonify

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

@app.route('/error', methods=['GET'])
def error():
    app.logger.error("A critical error occurred on /error endpoint!")
    return jsonify({"error": "Something went wrong"}), 500

if __name__ == '__main__':
    app.run(debug=True)