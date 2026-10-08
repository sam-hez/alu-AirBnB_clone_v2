# AirBnB clone - Web framework

This project uses Flask to serve the AirBnB application's web routes.
Each numbered Python file is a separate application.

Install Flask in your Python environment:

```bash
python3 -m pip install Flask
```

From the repository root, start task 0:

```bash
python3 -m web_flask.0-hello_route
```

The server listens on all interfaces at port 5000.
The home page returns exactly `Hello HBNB!`; an unknown route returns
HTTP 404. The route uses `strict_slashes=False`.

Test it from another terminal:

```bash
curl --noproxy '*' http://0.0.0.0:5000/
curl --noproxy '*' -i http://0.0.0.0:5000/noroute
```

Stop the server with Ctrl+C before starting another numbered application.

Task 1 adds `/hbnb`. Task 2 adds `/c/<text>`. Task 3 adds
`/python` and `/python/<text>`. Task 4 adds `/number/<int:n>`.
Task 5 adds `/number_template/<int:n>`, rendered through
`templates/5-number.html`.

## Tasks 6–10: parity, states, and cities

Run one application at a time from the repository root:

```bash
python3 -m web_flask.6-number_odd_or_even
python3 -m web_flask.7-states_list
python3 -m web_flask.8-cities_by_states
python3 -m web_flask.9-states
```

The file numbers follow the assignment: task 7 updates the storage
engines, so task 8 starts with `7-states_list.py`.

- `/number_odd_or_even/89` displays `Number: 89 is odd`.
- `/states_list` lists stored states alphabetically.
- `/cities_by_states` lists states and their cities alphabetically.
- `/states` lists states; `/states/<id>` displays one state's cities,
  or `Not found!` when the ID is unknown.

File storage is the default and reads `file.json` from the repository
root. Create and save State and City objects with the console first.
The state-backed applications also work with database storage:

```bash
HBNB_MYSQL_USER=hbnb_dev HBNB_MYSQL_PWD=hbnb_dev_pwd \
HBNB_MYSQL_HOST=localhost HBNB_MYSQL_DB=hbnb_dev_db \
HBNB_TYPE_STORAGE=db python3 -m web_flask.9-states
```

Prepare the database with `setup_mysql_dev.sql` before using database
storage. These applications use `storage.all(State)` and
`state.cities`, and call `storage.close()` after each request.
For JSON storage this reloads the file; for MySQL it releases the
current SQLAlchemy session.

## Task 11: HBNB filters

Run the filter page with file storage:

```bash
python3 -m web_flask.10-hbnb_filters
```

Or run it with the prepared MySQL database:

```bash
HBNB_MYSQL_USER=hbnb_dev HBNB_MYSQL_PWD=hbnb_dev_pwd \
HBNB_MYSQL_HOST=localhost HBNB_MYSQL_DB=hbnb_dev_db \
HBNB_TYPE_STORAGE=db python3 -m web_flask.10-hbnb_filters
```

Open `http://127.0.0.1:5000/hbnb_filters`. Hover over States to
see each state's cities, or over Amenities to see the amenity list.
All lists are alphabetical. Both menus scroll and have a maximum
height of 300px.

The page uses `storage.all(State)`, `state.cities`, and
`storage.all(Amenity)`, then closes storage after each request.
CSS and images are served from `web_flask/static/`.
The PNG favicon uses the existing ICO favicon's image.
The Search button is part of this task's layout.
