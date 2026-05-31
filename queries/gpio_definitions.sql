id INT IDENTITY PRIMARY KEY
router_id INT
config_pin NVARCHAR(20)
gpio_name NVARCHAR(255)
direction NVARCHAR(20)
high_state_name NVARCHAR(100)
low_state_name NVARCHAR(100)
status_key NVARCHAR(100)
enabled BIT
updated_at DATETIME2