@echo off
set "VC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"

if not exist "%VC_PATH%" (
    echo [ERROR] Nie znaleziono vcvarsall.bat. Sprawdz sciezke do Visual Studio.
    exit /b 1
)

call "%VC_PATH%" x64 >nul
cl /O2 /nologo /Fe:transformer.exe main.c
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Kompilacja zakonczona!
) else (
    echo [ERROR] Blad kompilacji.
)
