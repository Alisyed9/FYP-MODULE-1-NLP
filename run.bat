@echo off
echo.
echo ====================================================
echo   NLP Threat Classifier - Web Application Startup
echo ====================================================
echo.

REM Check if virtual environment exists
if not exist "nlp-env\Scripts\Activate.bat" (
    echo Error: Virtual environment not found!
    echo Please ensure nlp-env exists in this directory.
    pause
    exit /b 1
)

REM Activate virtual environment
call nlp-env\Scripts\Activate.bat

REM Install requirements if needed
echo.
echo Checking dependencies...
pip install -q --upgrade pip setuptools wheel
pip install -q -r requirements.txt

REM Download spacy model if not present
python -c "import spacy; spacy.load('en_core_web_sm')" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Installing spaCy language model...
    python -m spacy download en_core_web_sm
)

REM Start Flask app
cls
echo.
echo ====================================================
echo   ✓ Virtual environment activated
echo   ✓ Dependencies verified
echo   ✓ Starting Flask application...
echo.
echo   Web Interface: http://localhost:5000
echo.
echo   Press CTRL+C to stop the server
echo ====================================================
echo.

python app.py

pause
