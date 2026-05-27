@echo off
set "VC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"

if not exist "%VC_PATH%" (
    echo [ERROR] Nie znaleziono vcvarsall.bat. Sprawdz sciezke do Visual Studio.
    exit /b 1
)

echo [INFO] Inicjalizacja srodowiska MSVC dla CUDA...
call "%VC_PATH%" x64 >nul

echo [INFO] Kompilacja CUDA-Transformer...
nvcc -O3 -lcublas train_cuda.cu -o transformer_cuda.exe

if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Kompilacja CUDA zakonczona!
) else (
    echo [ERROR] Blad kompilacji CUDA.
)
