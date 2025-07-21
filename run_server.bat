@echo off
set PORT=8080
set PROJECT_NAME=inventory_django

REM === Detectar IP local ===
for /f "tokens=2 delims=:" %%f in ('ipconfig ^| findstr /c:"IPv4"') do (
    for /f "tokens=* delims= " %%a in ("%%f") do set IP=%%a
)
echo ===============================
echo Iniciando servidor Django...
echo URL Local:  http://127.0.0.1:%PORT%
echo URL Red:    http://%IP%:%PORT%
echo ===============================
echo.

REM === Iniciar Waitress ===
waitress-serve --listen=0.0.0.0:%PORT% %PROJECT_NAME%.wsgi:application

pause
