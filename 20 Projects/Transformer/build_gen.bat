@echo off
set "VC_PATH=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat"
call "%VC_PATH%" x64 >nul
nvcc -O3 -lcublas generate_cuda.cu -o generate_cuda.exe
if %ERRORLEVEL% equ 0 (
    echo [SUCCESS] Generator compiled!
    .\generate_cuda.exe
) else (
    echo [ERROR] Build failed.
)
