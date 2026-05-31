id INT IDENTITY PRIMARY KEY
router_id INT
gpio_definition_id INT
status_key NVARCHAR(100)
raw_value INT
human_status NVARCHAR(100)
is_alert BIT
checked_at DATETIME2