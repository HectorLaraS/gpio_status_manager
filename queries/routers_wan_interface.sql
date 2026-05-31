id INT IDENTITY PRIMARY KEY
router_id INT
uid NVARCHAR(100)
name NVARCHAR(255)
type NVARCHAR(50)
connection_state NVARCHAR(50)
ipv4_address NVARCHAR(50)
gateway NVARCHAR(50)
netmask NVARCHAR(50)
is_selected BIT
updated_at DATETIME2