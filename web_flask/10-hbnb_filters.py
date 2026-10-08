#!/usr/bin/python3
"""Display HBNB state, city, and amenity filters with Flask."""
from flask import Flask, render_template
from models import storage
from models.state import State
from models.amenity import Amenity


app = Flask(__name__)


@app.route('/hbnb_filters', strict_slashes=False)
def hbnb_filters():
    """Render the filters using states and amenities from storage."""
    states = storage.all(State).values()
    amenities = storage.all(Amenity).values()
    return render_template('10-hbnb_filters.html', states=states,
                           amenities=amenities)


@app.teardown_appcontext
def close_storage(error):
    """Release storage resources after each application context."""
    storage.close()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
