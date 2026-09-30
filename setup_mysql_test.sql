-- Create the isolated MySQL database and user for HBNB tests.
CREATE DATABASE IF NOT EXISTS hbnb_test_db;
-- Create the local test user without changing an existing account.
CREATE USER IF NOT EXISTS 'hbnb_test'@'localhost'
IDENTIFIED BY 'hbnb_test_pwd';
-- Allow this user to manage only the test database.
GRANT ALL PRIVILEGES ON hbnb_test_db.* TO 'hbnb_test'@'localhost';
-- Allow the metadata access required by the project.
GRANT SELECT ON performance_schema.* TO 'hbnb_test'@'localhost';
