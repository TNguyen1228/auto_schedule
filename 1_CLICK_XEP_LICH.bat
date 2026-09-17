@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title Tự Động Xếp Thời Khóa Biểu Tiểu Học

:: Chuyển thư mục làm việc về thư mục chứa file .bat
cd /d "%~dp0"

:: Tìm Python phù hợp
set "PYTHON_CMD="
if exist "%~dp0auto_schedule\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0auto_schedule\Scripts\python.exe"
) else if exist "%~dp0venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0venv\Scripts\python.exe"
) else if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_CMD=%~dp0.venv\Scripts\python.exe"
) else (
    where python >nul 2>&1
    if !errorlevel! equ 0 (
        set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [!] LỖI: Không tìm thấy Python trong máy tính!
    pause
    exit /b 1
)

echo ======================================================================
echo    ĐANG TIẾN HÀNH XẾP THỜI KHÓA BIỂU TỰ ĐỘNG (GOOGLE OR-TOOLS CP-SAT)
echo ======================================================================
echo.

"%PYTHON_CMD%" main.py

if !errorlevel! equ 0 (
    echo.
    echo ======================================================================
    echo [✓] ĐÃ XẾP THỜI KHÓA BIỂU THÀNH CÔNG!
    echo Đang tự động mở file kết quả Thoi_Khoa_Bieu_Truong_9_Lop.xlsx...
    echo ======================================================================
    if exist "Thoi_Khoa_Bieu_Truong_9_Lop.xlsx" (
        start "" "Thoi_Khoa_Bieu_Truong_9_Lop.xlsx"
    )
) else (
    echo.
    echo ======================================================================
    echo [!] CÓ LỖI XẢY RA TRONG QUÁ TRÌNH XẾP LỊCH. Vui lòng kiểm tra lại dữ liệu.
    echo ======================================================================
)

echo.
echo Nhấn phím bất kỳ để đóng cửa sổ này...
pause > nul

