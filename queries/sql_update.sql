USE CradlepointGPIO;
GO

IF COL_LENGTH('dbo.routers', 'resource_uri') IS NULL
BEGIN
    ALTER TABLE dbo.routers
    ADD resource_uri NVARCHAR(500) NULL;
END
GO

IF COL_LENGTH('dbo.router_wan_interfaces', 'last_successful_connection') IS NULL
BEGIN
    ALTER TABLE dbo.router_wan_interfaces
    ADD last_successful_connection DATETIME2 NULL;
END
GO