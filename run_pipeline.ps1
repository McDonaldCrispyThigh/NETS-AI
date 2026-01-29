# AI-BDD Pipeline Launcher Script

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.\AIAGENTNETS\Scripts\Activate.ps1

# Check dependencies
Write-Host "`nChecking dependencies..." -ForegroundColor Cyan
$packages = @("openai", "googlemaps", "waybackpy", "pandas", "python-dotenv")
foreach ($pkg in $packages) {
    python -c "import $($pkg.Replace('-', '_'))" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  Missing: $pkg" -ForegroundColor Red
        Write-Host "  Installing..." -ForegroundColor Yellow
        pip install $pkg
    } else {
        Write-Host "  OK: $pkg" -ForegroundColor Green
    }
}

# Check .env file
Write-Host "`nChecking environment variables..." -ForegroundColor Cyan
if (-not (Test-Path ".env")) {
    Write-Host "  .env file not found" -ForegroundColor Red
    Write-Host "  Creating template..." -ForegroundColor Yellow
    @"
OPENAI_API_KEY=your_openai_key_here
GOOGLE_MAPS_API_KEY=your_google_maps_key_here
"@ | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "  Created .env template - Please add your API keys" -ForegroundColor Yellow
    exit 1
}

# Validate API keys
$env_content = Get-Content ".env" -Raw
if ($env_content -match "your_openai_key_here" -or $env_content -match "your_google_maps_key_here") {
    Write-Host "  Please update .env with real API keys" -ForegroundColor Yellow
    exit 1
}
Write-Host "  API keys configured" -ForegroundColor Green

# Display menu
Write-Host "`n" + "="*60 -ForegroundColor Cyan
Write-Host "AI-BDD Complete Pipeline" -ForegroundColor Cyan
Write-Host "="*60 -ForegroundColor Cyan
Write-Host "`nSelect execution mode:" -ForegroundColor White
Write-Host "  1. List available categories" -ForegroundColor White
Write-Host "  2. Test run (10 locations)" -ForegroundColor White
Write-Host "  3. Full analysis: Coffee Shops" -ForegroundColor White
Write-Host "  4. Full analysis: Gyms" -ForegroundColor White
Write-Host "  5. Full analysis: Libraries" -ForegroundColor White
Write-Host "  6. Full analysis: Grocery Stores" -ForegroundColor White
Write-Host "  7. Custom execution" -ForegroundColor White
Write-Host ""

$choice = Read-Host "Enter option (1-7)"

switch ($choice) {
    "1" {
        python scripts/03_complete_pipeline.py --list
    }
    "2" {
        Write-Host "`nRunning test with 10 locations..." -ForegroundColor Yellow
        python scripts/03_complete_pipeline.py --task coffee --limit 10
    }
    "3" {
        Write-Host "`nAnalyzing Coffee Shops..." -ForegroundColor Yellow
        python scripts/03_complete_pipeline.py --task coffee
    }
    "4" {
        Write-Host "`nAnalyzing Gyms..." -ForegroundColor Yellow
        python scripts/03_complete_pipeline.py --task gym
    }
    "5" {
        Write-Host "`nAnalyzing Libraries..." -ForegroundColor Yellow
        python scripts/03_complete_pipeline.py --task library
    }
    "6" {
        Write-Host "`nAnalyzing Grocery Stores..." -ForegroundColor Yellow
        python scripts/03_complete_pipeline.py --task grocery
    }
    "7" {
        Write-Host "`nCustom execution options:" -ForegroundColor Cyan
        Write-Host "  --task <category>      : Business category" -ForegroundColor White
        Write-Host "  --limit <number>       : Limit places" -ForegroundColor White
        Write-Host "  --skip-wayback        : Skip Wayback validation" -ForegroundColor White
        Write-Host "  --skip-gpt            : Skip GPT analysis" -ForegroundColor White
        Write-Host ""
        $custom_args = Read-Host "Enter parameters"
        python scripts/03_complete_pipeline.py $custom_args.Split(" ")
    }
    default {
        Write-Host "`nInvalid option" -ForegroundColor Red
        exit 1
    }
}

Write-Host "`nExecution completed" -ForegroundColor Green
