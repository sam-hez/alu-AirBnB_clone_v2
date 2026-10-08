#!/usr/bin/python3
"""Display stored states through a Flask web application."""
from flask import Flask, render_template
from models import storage
from models.state import State


app = Flask(__name__)


@app.route('/states_list', strict_slashes=False)
def states_list():
    """Render states fetched from the selected storage engine."""
    states = storage.all(State).values()
    return render_template('7-states_list.html', states=states)


@app.teardown_appcontext
def close_storage(error):
    """Release storage resources after each application context."""
    storage.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
