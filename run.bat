@echo off
title Netflix Checker - Launcher
color 0E

echo ==================================================
echo   RUNNING NETFLIX PREMIUM COOKIE CHECKER
echo ==================================================
echo.

REM Cek apakah Python terinstall
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python tidak ditemukan!
    echo.
    echo 📌 Solusi:
    echo 1. Pastikan Python sudah terinstall.
    echo 2. Pastikan "Add Python to PATH" sudah dicentang saat install.
    echo 3. Restart Command Prompt, lalu coba lagi.
    echo.
    pause
    exit /b
)

REM Cek apakah file netfix_cli.py ada
if not exist "netfix_cli.py" (
    echo ❌ ERROR: File netfix_cli.py tidak ditemukan!
    echo.
    echo 📌 Solusi:
    echo 1. Pastikan Anda berada di folder yang benar.
    echo 2. Pastikan file netfix_cli.py ada di folder ini.
    echo 3. Jika tidak ada, download ulang atau buat file tersebut.
    echo.
    pause
    exit /b
)

echo ✅ Python terdeteksi. Menjalankan script...
echo.
echo ==================================================
echo   PRESS CTRL+C TO STOP SCANNING
echo ==================================================
echo.

REM Jalankan script
python netfix_cli.py

if errorlevel 1 (
    echo.
    echo ❌ Program berhenti dengan error.
    echo.
    echo 📌 Kemungkinan penyebab:
    echo 1. Library belum diinstall (jalankan install.bat dulu).
    echo 2. Ada error di dalam script netfix_cli.py.
    echo 3. Chrome tidak terinstall atau versinya tidak cocok.
    echo.
) else (
    echo.
    echo ==================================================
    echo ✅ Scan selesai! Cek folder active_account untuk hasil.
    echo ==================================================
)

echo.
echo Tekan tombol apa pun untuk keluar...
pause >nul
