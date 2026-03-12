# NLP Threat Classifier - PowerShell Startup Script

Write-Host ""
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host "  NLP Threat Classifier - Web Application Startup" -ForegroundColor Cyan
Write-Host "====================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "nlp-env\Scripts\Activate.ps1")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please ensure nlp-env exists in this directory."
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "nlp-env\Scripts\Activate.ps1"

# Check and install dependencies
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow
python -m pip install -q --upgrade pip setuptools wheel
pip install -q -r requirements.txt

# Download spacy model if needed
Write-Host "Verifying spaCy language model..." -ForegroundColor Yellow
$null = python -c "import spacy; spacy.load('en_core_web_sm')" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing spaCy language model..." -ForegroundColor Yellow
    python -m spacy download en_core_web_sm
}

# Clear and start Flask app
Clear-Host
Write-Host ""
Write-Host "====================================================" -ForegroundColor Green
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green
Write-Host "  ✓ Dependencies verified" -ForegroundColor Green
Write-Host "  ✓ Starting Flask application..." -ForegroundColor Green
Write-Host ""
Write-Host "  Web Interface: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host "====================================================" -ForegroundColor Green
Write-Host ""

# Start the Flask application
python app.py
