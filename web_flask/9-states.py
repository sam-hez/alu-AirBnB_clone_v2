#!/usr/bin/python3
"""Display all states or the cities of a selected state with Flask."""
from flask import Flask, render_template
from models import storage
from models.state import State


app = Flask(__name__)


@app.route('/states', strict_slashes=False)
@app.route('/states/<state_id>', strict_slashes=False)
def states(state_id=None):
    """Render the state list, a selected state, or a not-found message."""
    all_states = storage.all(State)
    state = all_states.get('State.' + state_id) if state_id else None
    return render_template('9-states.html', states=all_states.values(),
                           state=state, state_id=state_id)


@app.teardown_appcontext
def close_storage(error):
    """Release storage resources after each application context."""
    storage.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
