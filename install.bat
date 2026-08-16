@echo off
title Netflix Checker Auto Installer - by adooo
color 0A

echo ====================================================
echo   NETFLIX PREMIUM CHECKER - AUTO INSTALLER
echo   by adooo ;P
echo ====================================================
echo.

:: 1. Cek Python
echo [1/3] Mengecek Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python tidak ditemukan!
    echo Silakan download dan install Python dari python.org.
    echo (Jangan lupa centang "Add Python to PATH" saat install)
    echo.
    pause
    exit /b
)
echo [OK] Python ditemukan.
echo.

:: 2. Install Library (Menampilkan proses download di layar)
echo [2/3] Menginstall Selenium dan Webdriver-Manager...
echo.
pip install selenium webdriver-manager
echo.

:: 3. Buat folder
echo [3/3] Membuat struktur folder...
if not exist cookies mkdir cookies
if not exist active_account mkdir active_account
echo [OK] Folder cookies dan active_account siap.
echo.

echo ====================================================
echo   INSTALASI BERHASIL!
echo ====================================================
echo.
echo Sekarang Anda bisa klik ganda file "run.bat" untuk memulai scan.
echo.
pause