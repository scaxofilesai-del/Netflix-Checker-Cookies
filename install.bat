@echo off
title Netflix Checker - Installer
color 0A

echo ==================================================
echo   INSTALLING DEPENDENCIES FOR NETFLIX CHECKER
echo ==================================================
echo.

REM Cek apakah Python terinstall
echo [1/3] Mengecek Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python tidak ditemukan!
    echo.
    echo 📌 Solusi:
    echo 1. Download Python di https://www.python.org/downloads/
    echo 2. Install Python dengan mencentang "Add Python to PATH"
    echo 3. Restart Command Prompt, lalu jalankan install.bat lagi
    echo.
    pause
    exit /b
)
echo ✅ Python terdeteksi.
echo.

REM Install library yang dibutuhkan
echo [2/3] Menginstall library (selenium, webdriver-manager)...
pip install selenium webdriver-manager

if errorlevel 1 (
    echo.
    echo ❌ Gagal menginstall library.
    echo.
    echo 📌 Solusi:
    echo 1. Pastikan internet Anda terhubung.
    echo 2. Coba jalankan Command Prompt sebagai Administrator.
    echo 3. Lalu ketik: pip install selenium webdriver-manager
    echo.
    pause
    exit /b
)

echo.
echo ==================================================
echo ✅ Installation Complete!
echo ==================================================
echo.
echo Anda sekarang bisa menjalankan run.bat
echo.
pause
