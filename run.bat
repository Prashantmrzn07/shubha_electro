@echo off
cd /d "%~dp0"

set PYTHON_EXE=.\.venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
    echo Warning: .venv\Scripts\python.exe not found. Using system python.
)

echo Checking and applying database migrations...
"%PYTHON_EXE%" manage.py migrate

echo.
echo ========================================================
echo  Shuba Electronics Shopping System is ready!
echo  URL: http://127.0.0.1:8000/
echo  Customer portal: http://127.0.0.1:8000/accounts/login/
echo  Admin portal: http://127.0.0.1:8000/accounts/admin-login/
echo  Press Ctrl+C to stop the server
echo ========================================================
echo.

"%PYTHON_EXE%" manage.py runserver 127.0.0.1:8000
pause
