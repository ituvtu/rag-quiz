@echo off
REM Deploy RAG Quiz to Hugging Face Spaces (Windows)

echo.
echo 🚀 RAG Quiz HF Spaces Deployment
echo.

REM Check if huggingface-cli is installed
where huggingface-cli >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ huggingface-cli not found. Install with:
    echo pip install huggingface-hub
    exit /b 1
)

REM Check if .hfignore exists
if not exist ".hfignore" (
    echo ❌ .hfignore file not found
    exit /b 1
)

REM Get space name from user
set /p SPACE_NAME="Enter your HF Space name (e.g., username/rag-quiz): "

if "%SPACE_NAME%"=="" (
    echo ❌ Space name is required
    exit /b 1
)

echo.
echo 📤 Deploying to: %SPACE_NAME%
echo.

REM Push to HF Spaces
git push --force "https://huggingface.co/spaces/%SPACE_NAME%" main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Deployment successful!
    echo 📍 Space URL: https://huggingface.co/spaces/%SPACE_NAME%
    echo.
) else (
    echo.
    echo ❌ Deployment failed
    exit /b 1
)
