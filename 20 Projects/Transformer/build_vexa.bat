@echo off
set "VC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
call "%VC_PATH%" x64 >nul
if exist vexa_trinity.exe del vexa_trinity.exe
nvcc -O3 -arch=sm_89 -lcublas vexa_all_in_one.cu -o vexa_trinity.exe
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Compiled!
    .\vexa_trinity.exe
) else (
    echo [ERROR] nvcc failed.
)
