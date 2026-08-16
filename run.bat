@echo off
title Netflix Premium Checker - by adooo
color 0A

echo ====================================================
echo   MENJALANKAN NETFLIX PREMIUM CHECKER
echo   by adooo ;P
echo ====================================================
echo.
echo Memastikan library sudah terinstall...
python -c "import selenium" >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [PERINGATAN] Library Selenium belum diinstall.
    echo Silakan klik ganda file "install.bat" terlebih dahulu.
    echo.
    pause
    exit /b
)
echo.
echo Menjalankan Bot...
echo.
python netfix_cli.py
echo.
pause