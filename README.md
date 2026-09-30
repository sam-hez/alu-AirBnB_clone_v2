# alu-AirBnB_clone_v2 - MySQL project

Maintained for the ALU project by **sam-hez**
(<h.epodoi@alustudent.com>).

Repository: https://github.com/sam-hez/alu-AirBnB_clone_v2

This fork builds on the original console and web static project by
**Ezra Nobrega** and **Justin Majetich**. Their documentation is preserved
below, and their names remain in [AUTHORS](AUTHORS).

## Storage and testing

File storage is the default. Database storage uses SQLAlchemy 1.4 and MySQL 8.
Install the dependencies with `python3 -m pip install -r requirements.txt`.
On Ubuntu, building mysqlclient requires `python3-dev`, `build-essential`,
`pkg-config`, and `default-libmysqlclient-dev`.

Run file tests and the style check from the repository directory:

```bash
python3 -m unittest discover tests
pycodestyle console.py models tests
```

Create the test database using a MySQL administrator account:

```bash
mysql -u root -p < setup_mysql_test.sql
```

Run the database tests:

```bash
HBNB_ENV=test HBNB_MYSQL_USER=hbnb_test HBNB_MYSQL_PWD=hbnb_test_pwd \
HBNB_MYSQL_HOST=localhost HBNB_MYSQL_DB=hbnb_test_db HBNB_TYPE_STORAGE=db \
python3 -m unittest discover tests
```

`HBNB_MYSQL_PORT` defaults to 3306 and can be changed for a local test server.
`HBNB_ENV=test` resets mapped tables when storage starts. Use it only with
an expendable test database. The integration fixtures require `hbnb_test_db`
and verify database changes using the MySQL driver directly. File-only and
database-only tests use `unittest.skipIf` in the other storage mode.
File tests use temporary JSON files and preserve existing saved data.

Examples supported by both engines:

```text
create State name="New_York"
all State
update State <id> name "California"
destroy State <id>
```

BaseModel is the shared parent class and has no table in database mode.
City, Place, and Review require valid IDs for their referenced objects.

## Creating objects with parameters

Use `create <Class> key=value ...`. Types come from the value syntax:

- Double-quoted values are strings; underscores become spaces.
- Escape a double quote inside a string with a backslash.
- Unquoted values containing a dot are floats; other numbers are integers.
- Invalid parameters are skipped while valid parameters are saved.

```text
create State name="California"
create Place city_id="0001" user_id="0001" name="My_little_house" number_rooms=4 latitude=37.773972 longitude=-122.431297
```

The Place example uses sample IDs for file storage. Database storage requires
IDs that reference existing City and User rows.

## Development database setup

Run the development setup script with a MySQL administrator account:

```bash
mysql -hlocalhost -uroot -p < setup_mysql_dev.sql
```

It creates `hbnb_dev_db` and the local user `hbnb_dev` with password
`hbnb_dev_pwd`. The user receives all privileges on `hbnb_dev_db` and only
SELECT on `performance_schema`. Rerunning the script preserves existing data
and sets the required development password again.

Start a development console with:

```bash
HBNB_MYSQL_USER=hbnb_dev HBNB_MYSQL_PWD=hbnb_dev_pwd \
HBNB_MYSQL_HOST=localhost HBNB_MYSQL_DB=hbnb_dev_db HBNB_TYPE_STORAGE=db \
python3 console.py
```

Keep `HBNB_ENV=test` for the separate test database; it resets mapped tables.

## Original project documentation

<center> <h1>HBNB - The Console</h1> </center>

This repository contains the initial stage of a student project to build a clone of the AirBnB website. This stage implements a backend interface, or console, to manage program data. Console commands allow the user to create, update, and destroy objects, as well as manage file storage. Using a system of JSON serialization/deserialization, storage is persistent between sessions.

---

<center><h3>Repository Contents by Project Task</h3> </center>

| Tasks | Files | Description |
| ----- | ----- | ------ |
| 0: Authors/README File | [AUTHORS](AUTHORS) | Project authors |
| 1: Pep8 | N/A | All code is pep8 compliant|
| 2: Unit Testing | [/tests](tests) | All class-defining modules are unittested |
| 3. Make BaseModel | [/models/base_model.py](models/base_model.py) | Defines a parent class to be inherited by all model classes|
| 4. Update BaseModel w/ kwargs | [/models/base_model.py](models/base_model.py) | Add functionality to recreate an instance of a class from a dictionary representation|
| 5. Create FileStorage class | [/models/engine/file_storage.py](models/engine/file_storage.py) [/models/_ _init_ _.py](models/__init__.py) [/models/base_model.py](models/base_model.py) | Defines a class to manage persistent file storage system|
| 6. Console 0.0.1 | [console.py](console.py) | Add basic functionality to console program, allowing it to quit, handle empty lines and ^D |
| 7. Console 0.1 | [console.py](console.py) | Update the console with methods allowing the user to create, destroy, show, and update stored data |
| 8. Create User class | [console.py](console.py) [/models/engine/file_storage.py](models/engine/file_storage.py) [/models/user.py](models/user.py) | Dynamically implements a user class |
| 9. More Classes | [/models/user.py](models/user.py) [/models/place.py](models/place.py) [/models/city.py](models/city.py) [/models/amenity.py](models/amenity.py) [/models/state.py](models/state.py) [/models/review.py](models/review.py) | Dynamically implements more classes |
| 10. Console 1.0 | [console.py](console.py) [/models/engine/file_storage.py](models/engine/file_storage.py) | Update the console and file storage system to work dynamically with all  classes update file storage |
<br>
<br>
<center> <h2>General Use</h2> </center>

1. First clone this repository.

3. Once the repository is cloned locate the "console.py" file and run it as follows:
```
/AirBnB_clone$ ./console.py
```
4. When this command is run the following prompt should appear:
```
(hbnb)
```
5. This prompt designates you are in the "HBnB" console. There are a variety of commands available within the console program.

##### Commands
    * create - Creates an instance based on given class

    * destroy - Destroys an object based on class and UUID

    * show - Shows an object based on class and UUID

    * all - Shows all objects the program has access to, or all objects of a given class

    * update - Updates existing attributes an object based on class name and UUID

    * quit - Exits the program (EOF will as well)


##### Alternative Syntax
Users are able to issue a number of console command using an alternative syntax:

	Usage: <class_name>.<command>([<id>[name_arg value_arg]|[kwargs]])
Advanced syntax is implemented for the following commands: 

    * all - Shows all objects the program has access to, or all objects of a given class

	* count - Return number of object instances by class

    * show - Shows an object based on class and UUID

	* destroy - Destroys an object based on class and UUID

    * update - Updates existing attributes an object based on class name and UUID

<br>
<br>
<center> <h2>Examples</h2> </center>
<h3>Primary Command Syntax</h3>

###### Example 0: Create an object
Usage: create <class_name>
```
(hbnb) create BaseModel
```
```
(hbnb) create BaseModel
3aa5babc-efb6-4041-bfe9-3cc9727588f8
(hbnb)                   
```
###### Example 1: Show an object
Usage: show <class_name> <_id>

```
(hbnb) show BaseModel 3aa5babc-efb6-4041-bfe9-3cc9727588f8
[BaseModel] (3aa5babc-efb6-4041-bfe9-3cc9727588f8) {'id': '3aa5babc-efb6-4041-bfe9-3cc9727588f8', 'created_at': datetime.datetime(2020, 2, 18, 14, 21, 12, 96959), 
'updated_at': datetime.datetime(2020, 2, 18, 14, 21, 12, 96971)}
(hbnb)  
```
###### Example 2: Destroy an object
Usage: destroy <class_name> <_id>
```
(hbnb) destroy BaseModel 3aa5babc-efb6-4041-bfe9-3cc9727588f8
(hbnb) show BaseModel 3aa5babc-efb6-4041-bfe9-3cc9727588f8
** no instance found **
(hbnb)   
```
###### Example 3: Update an object
Usage: update <class_name> <_id>
```
(hbnb) update BaseModel b405fc64-9724-498f-b405-e4071c3d857f first_name "person"
(hbnb) show BaseModel b405fc64-9724-498f-b405-e4071c3d857f
[BaseModel] (b405fc64-9724-498f-b405-e4071c3d857f) {'id': 'b405fc64-9724-498f-b405-e4071c3d857f', 'created_at': datetime.datetime(2020, 2, 18, 14, 33, 45, 729889), 
'updated_at': datetime.datetime(2020, 2, 18, 14, 33, 45, 729907), 'first_name': 'person'}
(hbnb)
```
<h3>Alternative Syntax</h3>

###### Example 0: Show all User objects
Usage: <class_name>.all()
```
(hbnb) User.all()
["[User] (99f45908-1d17-46d1-9dd2-b7571128115b) {'updated_at': datetime.datetime(2020, 2, 19, 21, 47, 34, 92071), 'id': '99f45908-1d17-46d1-9dd2-b7571128115b', 'created_at': datetime.datetime(2020, 2, 19, 21, 47, 34, 92056)}", "[User] (98bea5de-9cb0-4d78-8a9d-c4de03521c30) {'updated_at': datetime.datetime(2020, 2, 19, 21, 47, 29, 134362), 'id': '98bea5de-9cb0-4d78-8a9d-c4de03521c30', 'created_at': datetime.datetime(2020, 2, 19, 21, 47, 29, 134343)}"]
```

###### Example 1: Destroy a User
Usage: <class_name>.destroy(<_id>)
```
(hbnb) User.destroy("99f45908-1d17-46d1-9dd2-b7571128115b")
(hbnb)
(hbnb) User.all()
(hbnb) ["[User] (98bea5de-9cb0-4d78-8a9d-c4de03521c30) {'updated_at': datetime.datetime(2020, 2, 19, 21, 47, 29, 134362), 'id': '98bea5de-9cb0-4d78-8a9d-c4de03521c30', 'created_at': datetime.datetime(2020, 2, 19, 21, 47, 29, 134343)}"]
```
###### Example 2: Update User (by attribute)
Usage: <class_name>.update(<_id>, <attribute_name>, <attribute_value>)
```
(hbnb) User.update("98bea5de-9cb0-4d78-8a9d-c4de03521c30", name "Todd the Toad")
(hbnb)
(hbnb) User.all()
(hbnb) ["[User] (98bea5de-9cb0-4d78-8a9d-c4de03521c30) {'updated_at': datetime.datetime(2020, 2, 19, 21, 47, 29, 134362), 'id': '98bea5de-9cb0-4d78-8a9d-c4de03521c30', 'name': 'Todd the Toad', 'created_at': datetime.datetime(2020, 2, 19, 21, 47, 29, 134343)}"]
```
###### Example 3: Update User (by dictionary)
Usage: <class_name>.update(<_id>, <dictionary>)
```
(hbnb) User.update("98bea5de-9cb0-4d78-8a9d-c4de03521c30", {'name': 'Fred the Frog', 'age': 9})
(hbnb)
(hbnb) User.all()
(hbnb) ["[User] (98bea5de-9cb0-4d78-8a9d-c4de03521c30) {'updated_at': datetime.datetime(2020, 2, 19, 21, 47, 29, 134362), 'name': 'Fred the Frog', 'age': 9, 'id': '98bea5de-9cb0-4d78-8a9d-c4de03521c30', 'created_at': datetime.datetime(2020, 2, 19, 21, 47, 29, 134343)}"]
```
<br>


## Storage and State cities

Create an object, then call `save()` to add it to storage and persist it.
`storage.all(State)` returns a dictionary containing only states.
`storage.delete(obj)` removes an object; call `storage.save()` to persist
the deletion. Calling `storage.delete()` without an object does nothing.

With file storage, `state.cities` is a read-only list of stored cities whose
`state_id` matches the state. With database storage, `state.cities` and
`city.state` use a SQLAlchemy relationship. Deleting a state also deletes
its related cities when the transaction is committed.

## Users and Places in MySQL

Users require an email and password; first and last names are optional.
Places require a name, a valid city ID, and a valid user ID. Room counts,
bathroom counts, maximum guests, and nightly prices default to zero.
Description, latitude, and longitude may be NULL.

A user's places are available through `user.places`, with `place.user`
pointing back to the user. A city's places are available through
`city.places`, with `place.cities` pointing back to the city.
Deleting a user or city also deletes its related places on commit.
