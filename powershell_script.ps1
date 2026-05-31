# ==========================================================
# Cradlepoint GPIO Monitor - Project Bootstrap
# ==========================================================

$ProjectName = "gpio_status_manager"

Write-Host "Creating project structure..." -ForegroundColor Green

# Root
New-Item -ItemType Directory -Force -Path $ProjectName | Out-Null

# Main directories
$directories = @(
    "$ProjectName\src",
    "$ProjectName\src\clients",
    "$ProjectName\src\services",
    "$ProjectName\src\repositories",
    "$ProjectName\src\web",
    "$ProjectName\src\web\templates",
    "$ProjectName\src\web\static",
    "$ProjectName\src\utils",
    "$ProjectName\src\models",
    "$ProjectName\config",
    "$ProjectName\sql",
    "$ProjectName\logs"
)

foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

# Python files
$pythonFiles = @(
    "$ProjectName\src\__init__.py",

    "$ProjectName\src\main.py",
    "$ProjectName\src\config.py",

    "$ProjectName\src\clients\netcloud_client.py",
    "$ProjectName\src\clients\ncos_client.py",

    "$ProjectName\src\services\group_service.py",
    "$ProjectName\src\services\router_service.py",
    "$ProjectName\src\services\wan_service.py",
    "$ProjectName\src\services\gpio_service.py",
    "$ProjectName\src\services\poll_service.py",

    "$ProjectName\src\repositories\db.py",
    "$ProjectName\src\repositories\group_repository.py",
    "$ProjectName\src\repositories\router_repository.py",
    "$ProjectName\src\repositories\wan_repository.py",
    "$ProjectName\src\repositories\gpio_repository.py",

    "$ProjectName\src\utils\gpio_mapper.py",
    "$ProjectName\src\utils\logger.py",

    "$ProjectName\src\models\group.py",
    "$ProjectName\src\models\router.py",
    "$ProjectName\src\models\gpio.py",

    "$ProjectName\src\web\app.py",
    "$ProjectName\src\web\routes.py"
)

foreach ($file in $pythonFiles) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}

# HTML templates
$templateFiles = @(
    "$ProjectName\src\web\templates\login.html",
    "$ProjectName\src\web\templates\dashboard.html",
    "$ProjectName\src\web\templates\router_detail.html"
)

foreach ($file in $templateFiles) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}

# Static files
$staticFiles = @(
    "$ProjectName\src\web\static\style.css",
    "$ProjectName\src\web\static\dashboard.js"
)

foreach ($file in $staticFiles) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}

# Config files
$configFiles = @(
    "$ProjectName\config\gpio_profiles.json",
    "$ProjectName\.env",
    "$ProjectName\.env.example",
    "$ProjectName\requirements.txt"
)

foreach ($file in $configFiles) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}

# SQL files
$sqlFiles = @(
    "$ProjectName\sql\01_schema.sql",
    "$ProjectName\sql\02_seed_groups.sql"
)

foreach ($file in $sqlFiles) {
    New-Item -ItemType File -Force -Path $file | Out-Null
}

Write-Host ""
Write-Host "Project structure created successfully." -ForegroundColor Green
Write-Host ""
Write-Host "Project: $ProjectName"