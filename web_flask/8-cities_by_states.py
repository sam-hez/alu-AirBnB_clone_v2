#!/usr/bin/python3
"""Display stored states through a Flask web application."""
from flask import Flask, render_template
from models import storage
from models.state import State


app = Flask(__name__)


@app.route('/cities_by_states', strict_slashes=False)
def cities_by_states():
    """Render states fetched from the selected storage engine."""
    states = storage.all(State).values()
    return render_template('8-cities_by_states.html', states=states)


@app.teardown_appcontext
def close_storage(error):
    """Release storage resources after each application context."""
    storage.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
