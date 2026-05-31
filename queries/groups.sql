CREATE DATABASE CradlepointGPIO;
GO

USE CradlepointGPIO;
GO

id INT IDENTITY PRIMARY KEY
netcloud_id INT UNIQUE
name NVARCHAR(255)
is_active BIT
created_at DATETIME2
updated_at DATETIME2