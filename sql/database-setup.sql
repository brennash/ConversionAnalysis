CREATE DATABASE IF NOT EXISTS conversions;
CREATE USER 'conversions'@'localhost' IDENTIFIED BY 'conversions';
GRANT ALL PRIVILEGES ON conversions.* TO 'conversions'@'localhost';
FLUSH PRIVILEGES;
