@echo off
echo ===================================================
echo Starting InterviewIQ AI FastAPI Server...
echo ===================================================
cd /d "%~dp0"

set PYTHON_PATH="C:\Users\brgoj\AppData\Local\Programs\Python\Python313\python.exe"

if exist %PYTHON_PATH% (
    %PYTHON_PATH% -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) else (
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
)

pause

