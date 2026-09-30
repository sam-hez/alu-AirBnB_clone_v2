-- Prepare the HBNB development database and its local user.
CREATE DATABASE IF NOT EXISTS hbnb_dev_db;
-- Create the development user if it does not already exist.
CREATE USER IF NOT EXISTS 'hbnb_dev'@'localhost'
IDENTIFIED BY 'hbnb_dev_pwd';
-- Set the required password even when the user already exists.
ALTER USER 'hbnb_dev'@'localhost' IDENTIFIED BY 'hbnb_dev_pwd';
-- Allow the development user to manage the development database.
GRANT ALL PRIVILEGES ON hbnb_dev_db.* TO 'hbnb_dev'@'localhost';
-- Allow read access to performance metadata only.
GRANT SELECT ON performance_schema.* TO 'hbnb_dev'@'localhost';
