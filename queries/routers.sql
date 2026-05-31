id INT IDENTITY PRIMARY KEY
netcloud_id INT UNIQUE
group_id INT
name NVARCHAR(255)
state NVARCHAR(50)
config_status NVARCHAR(50)
full_product_name NVARCHAR(255)
is_active BIT
last_seen_at DATETIME2
updated_at DATETIME2