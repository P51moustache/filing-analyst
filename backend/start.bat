@echo off
REM 10-K Analysis Backend Start Script for Windows

echo Starting 10-K Analysis Backend...

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found!
    echo Please run setup first:
    echo   python -m venv venv
    echo   venv\Scripts\activate
    echo   pip install -r requirements.txt
    exit /b 1
)

REM Check if .env exists
if not exist ".env" (
    echo .env file not found!
    echo Please create .env file with your Anthropic API key:
    echo   copy .env.example .env
    echo   REM Then edit .env and add your API key
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate

REM Create necessary directories
if not exist "uploads\" mkdir uploads
if not exist "reports\" mkdir reports

REM Start the server
echo Starting FastAPI server on http://localhost:8000
echo API documentation: http://localhost:8000/docs
echo.
uvicorn main:app --reload
