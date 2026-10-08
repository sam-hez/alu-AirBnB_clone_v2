#!/usr/bin/python3
"""Start a Flask application with the Hello HBNB route."""
from flask import Flask


app = Flask(__name__)


@app.route('/', strict_slashes=False)
def hello_hbnb():
    """Return the greeting displayed on the home page."""
    return 'Hello HBNB!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
