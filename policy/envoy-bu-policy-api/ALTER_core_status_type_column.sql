-- Migration to extend core_status.type column to support longer type values
-- Run this SQL command on your database before seeding statuses

-- For MySQL/MariaDB:
ALTER TABLE core_status MODIFY COLUMN type VARCHAR(50) NOT NULL;

-- For PostgreSQL:
-- ALTER TABLE core_status ALTER COLUMN type TYPE VARCHAR(50);

-- For SQL Server:
-- ALTER TABLE core_status ALTER COLUMN type VARCHAR(50) NOT NULL;

