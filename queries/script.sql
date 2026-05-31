/* ============================================================
   Cradlepoint GPIO Monitor - Initial Database Script
   Database: CradlepointGPIO
   ============================================================ */

IF DB_ID('CradlepointGPIO') IS NULL
BEGIN
    CREATE DATABASE CradlepointGPIO;
END
GO

USE CradlepointGPIO;
GO

/* ============================================================
   USERS
   ============================================================ */

IF OBJECT_ID('dbo.app_users', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.app_users (
        id INT IDENTITY(1,1) PRIMARY KEY,
        username NVARCHAR(100) NOT NULL UNIQUE,
        password_hash NVARCHAR(255) NOT NULL,
        role_name NVARCHAR(50) NOT NULL DEFAULT 'viewer',
        is_active BIT NOT NULL DEFAULT 1,
        must_change_password BIT NOT NULL DEFAULT 0,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO

/* ============================================================
   NETCLOUD GROUPS
   ============================================================ */

IF OBJECT_ID('dbo.groups', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.groups (
        id INT IDENTITY(1,1) PRIMARY KEY,
        netcloud_id INT NOT NULL UNIQUE,
        name NVARCHAR(255) NOT NULL,
        is_active BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
    );
END
GO

/* ============================================================
   ROUTERS
   ============================================================ */

IF OBJECT_ID('dbo.routers', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.routers (
        id INT IDENTITY(1,1) PRIMARY KEY,
        netcloud_id INT NOT NULL UNIQUE,
        group_id INT NULL,
        name NVARCHAR(255) NULL,
        state NVARCHAR(50) NULL,
        description NVARCHAR(500) NULL,
        config_status NVARCHAR(50) NULL,
        full_product_name NVARCHAR(255) NULL,
        mac NVARCHAR(50) NULL,
        serial_number NVARCHAR(100) NULL,
        asset_id NVARCHAR(255) NULL,
        is_active BIT NOT NULL DEFAULT 1,
        last_seen_at DATETIME2 NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_routers_groups
            FOREIGN KEY (group_id)
            REFERENCES dbo.groups(id)
    );
END
GO

CREATE INDEX IX_routers_group_id
ON dbo.routers(group_id);
GO

CREATE INDEX IX_routers_state
ON dbo.routers(state);
GO

/* ============================================================
   ROUTER WAN INTERFACES
   ============================================================ */

IF OBJECT_ID('dbo.router_wan_interfaces', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.router_wan_interfaces (
        id INT IDENTITY(1,1) PRIMARY KEY,
        router_id INT NOT NULL,
        uid NVARCHAR(100) NULL,
        name NVARCHAR(255) NULL,
        interface_type NVARCHAR(50) NULL,
        connection_state NVARCHAR(50) NULL,
        summary NVARCHAR(255) NULL,
        ipv4_address NVARCHAR(50) NULL,
        gateway NVARCHAR(50) NULL,
        netmask NVARCHAR(50) NULL,
        dns_primary NVARCHAR(50) NULL,
        dns_secondary NVARCHAR(50) NULL,
        is_selected BIT NOT NULL DEFAULT 0,
        checked_at DATETIME2 NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_router_wan_interfaces_routers
            FOREIGN KEY (router_id)
            REFERENCES dbo.routers(id)
            ON DELETE CASCADE
    );
END
GO

CREATE INDEX IX_router_wan_interfaces_router_id
ON dbo.router_wan_interfaces(router_id);
GO

CREATE INDEX IX_router_wan_interfaces_ipv4
ON dbo.router_wan_interfaces(ipv4_address);
GO

/* ============================================================
   GPIO DEFINITIONS
   Configuration discovered from configuration_manager
   ============================================================ */

IF OBJECT_ID('dbo.gpio_definitions', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.gpio_definitions (
        id INT IDENTITY(1,1) PRIMARY KEY,
        router_id INT NOT NULL,
        config_pin NVARCHAR(20) NOT NULL,
        gpio_name NVARCHAR(255) NULL,
        direction NVARCHAR(20) NULL,
        high_state_name NVARCHAR(100) NULL,
        low_state_name NVARCHAR(100) NULL,
        alert_state NVARCHAR(50) NULL,
        debounce INT NULL,
        status_key NVARCHAR(100) NULL,
        profile_name NVARCHAR(100) NULL,
        enabled BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_gpio_definitions_routers
            FOREIGN KEY (router_id)
            REFERENCES dbo.routers(id)
            ON DELETE CASCADE,

        CONSTRAINT UQ_gpio_definitions_router_pin
            UNIQUE (router_id, config_pin)
    );
END
GO

CREATE INDEX IX_gpio_definitions_router_id
ON dbo.gpio_definitions(router_id);
GO

CREATE INDEX IX_gpio_definitions_status_key
ON dbo.gpio_definitions(status_key);
GO

/* ============================================================
   GPIO CURRENT STATUS
   Latest GPIO status per GPIO definition
   ============================================================ */

IF OBJECT_ID('dbo.gpio_status_current', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.gpio_status_current (
        id INT IDENTITY(1,1) PRIMARY KEY,
        router_id INT NOT NULL,
        gpio_definition_id INT NOT NULL,
        status_key NVARCHAR(100) NULL,
        raw_value INT NULL,
        human_status NVARCHAR(100) NULL,
        is_alert BIT NOT NULL DEFAULT 0,
        checked_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_gpio_status_current_routers
            FOREIGN KEY (router_id)
            REFERENCES dbo.routers(id)
            ON DELETE CASCADE,

        CONSTRAINT FK_gpio_status_current_definitions
            FOREIGN KEY (gpio_definition_id)
            REFERENCES dbo.gpio_definitions(id),

        CONSTRAINT UQ_gpio_status_current_definition
            UNIQUE (gpio_definition_id)
    );
END
GO

CREATE INDEX IX_gpio_status_current_router_id
ON dbo.gpio_status_current(router_id);
GO

CREATE INDEX IX_gpio_status_current_is_alert
ON dbo.gpio_status_current(is_alert);
GO

/* ============================================================
   POLL EXECUTIONS
   One row per polling cycle
   ============================================================ */

IF OBJECT_ID('dbo.poll_executions', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.poll_executions (
        id INT IDENTITY(1,1) PRIMARY KEY,
        execution_id UNIQUEIDENTIFIER NOT NULL DEFAULT NEWID(),
        started_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
        finished_at DATETIME2 NULL,
        status NVARCHAR(50) NOT NULL DEFAULT 'running',
        groups_processed INT NOT NULL DEFAULT 0,
        routers_processed INT NOT NULL DEFAULT 0,
        routers_success INT NOT NULL DEFAULT 0,
        routers_failed INT NOT NULL DEFAULT 0,
        notes NVARCHAR(MAX) NULL
    );
END
GO

CREATE UNIQUE INDEX UX_poll_executions_execution_id
ON dbo.poll_executions(execution_id);
GO

CREATE INDEX IX_poll_executions_started_at
ON dbo.poll_executions(started_at);
GO

/* ============================================================
   POLL LOGS
   Detailed logs by execution/router
   ============================================================ */

IF OBJECT_ID('dbo.poll_logs', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.poll_logs (
        id INT IDENTITY(1,1) PRIMARY KEY,
        execution_id UNIQUEIDENTIFIER NOT NULL,
        router_id INT NULL,
        level_name NVARCHAR(20) NOT NULL,
        source NVARCHAR(100) NULL,
        message NVARCHAR(MAX) NOT NULL,
        created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_poll_logs_routers
            FOREIGN KEY (router_id)
            REFERENCES dbo.routers(id)
            ON DELETE SET NULL
    );
END
GO

CREATE INDEX IX_poll_logs_execution_id
ON dbo.poll_logs(execution_id);
GO

CREATE INDEX IX_poll_logs_created_at
ON dbo.poll_logs(created_at);
GO

CREATE INDEX IX_poll_logs_level
ON dbo.poll_logs(level_name);
GO

/* ============================================================
   OPTIONAL GPIO HISTORY
   Disabled logically, but table ready for future use
   ============================================================ */

IF OBJECT_ID('dbo.gpio_status_history', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.gpio_status_history (
        id BIGINT IDENTITY(1,1) PRIMARY KEY,
        router_id INT NOT NULL,
        gpio_definition_id INT NOT NULL,
        status_key NVARCHAR(100) NULL,
        raw_value INT NULL,
        human_status NVARCHAR(100) NULL,
        is_alert BIT NOT NULL DEFAULT 0,
        checked_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_gpio_status_history_routers
            FOREIGN KEY (router_id)
            REFERENCES dbo.routers(id)
            ON DELETE CASCADE,

        CONSTRAINT FK_gpio_status_history_definitions
            FOREIGN KEY (gpio_definition_id)
            REFERENCES dbo.gpio_definitions(id)
    );
END
GO

CREATE INDEX IX_gpio_status_history_router_checked
ON dbo.gpio_status_history(router_id, checked_at DESC);
GO

CREATE INDEX IX_gpio_status_history_alert
ON dbo.gpio_status_history(is_alert, checked_at DESC);
GO

/* ============================================================
   DASHBOARD VIEW
   ============================================================ */

CREATE OR ALTER VIEW dbo.vw_router_dashboard AS
SELECT
    r.id AS router_db_id,
    r.netcloud_id AS router_netcloud_id,
    r.name AS router_name,
    g.name AS group_name,
    r.state,
    r.config_status,
    r.full_product_name,
    wan.ipv4_address AS selected_wan_ip,
    wan.connection_state AS wan_connection_state,
    COUNT(gsc.id) AS gpio_count,
    SUM(CASE WHEN gsc.is_alert = 1 THEN 1 ELSE 0 END) AS gpio_alert_count,
    MAX(gsc.checked_at) AS last_gpio_check
FROM dbo.routers r
LEFT JOIN dbo.groups g
    ON r.group_id = g.id
LEFT JOIN dbo.router_wan_interfaces wan
    ON r.id = wan.router_id
    AND wan.is_selected = 1
LEFT JOIN dbo.gpio_status_current gsc
    ON r.id = gsc.router_id
GROUP BY
    r.id,
    r.netcloud_id,
    r.name,
    g.name,
    r.state,
    r.config_status,
    r.full_product_name,
    wan.ipv4_address,
    wan.connection_state;
GO

/* ============================================================
   SAMPLE QUERY
   ============================================================ */

SELECT *
FROM dbo.vw_router_dashboard
ORDER BY group_name, router_name;
GO