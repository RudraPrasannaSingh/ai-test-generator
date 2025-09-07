@echo off
echo 🚀 Starting AI Test Generator...
call venv\Scripts\activate.bat
uvicorn app.main:app --reload --port 8000
pause
