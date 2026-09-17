@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
title Hệ Thống Xếp Thời Khóa Biểu Tiểu Học Tự Động

:: Chuyển thư mục làm việc về thư mục chứa file .bat
cd /d "%~dp0"

:: 1. Tìm Python phù hợp
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
    echo ======================================================================
    echo [!] LỖI: Không tìm thấy Python hoặc môi trường ảo trong máy!
    echo Vui lòng cài đặt Python hoặc liên hệ quản trị viên để được hỗ trợ.
    echo ======================================================================
    pause
    exit /b 1
)

:MENU
cls
echo ======================================================================
echo          HỆ THỐNG XẾP THỜI KHÓA BIỂU TIỂU HỌC TỰ ĐỘNG
echo          (Sử dụng Google OR-Tools CP-SAT - Ràng buộc chuẩn Bộ GD)
echo ======================================================================
echo.
echo   [1] 🚀 XẾP THỜI KHÓA BIỂU NGAY (Tự động đọc dữ liệu ^& mở file kết quả)
echo   [2] 🔄 Đồng bộ sheet 'Phan_Cong' từ 3 bảng nguồn (Khung, Lớp, Bộ môn)
echo   [3] 📂 Mở file Excel Dữ liệu đầu vào (Input_Mau_TKB.xlsx)
echo   [4] 📊 Mở file Excel Thời khóa biểu kết quả (Thoi_Khoa_Bieu_Truong_9_Lop.xlsx)
echo   [5] 📝 Khởi tạo lại file Excel mẫu chuẩn ban đầu
echo   [0] ❌ Thoát
echo.
echo ======================================================================
set /p "CHOICE=>> Nhập lựa chọn của bạn (Mặc định ấn Enter là [1]): "

if "%CHOICE%"=="" set "CHOICE=1"
if "%CHOICE%"=="1" goto XEP_LICH
if "%CHOICE%"=="2" goto DONG_BO
if "%CHOICE%"=="3" goto MO_INPUT
if "%CHOICE%"=="4" goto MO_OUTPUT
if "%CHOICE%"=="5" goto TAO_MAU
if "%CHOICE%"=="0" goto KET_THUC

echo.
echo [!] Lựa chọn không hợp lệ. Vui lòng chọn từ 0 đến 5.
timeout /t 2 > nul
goto MENU

:XEP_LICH
cls
echo ======================================================================
echo ĐANG TIẾN HÀNH XẾP THỜI KHÓA BIỂU...
echo ======================================================================
echo.
"%PYTHON_CMD%" main.py
if !errorlevel! equ 0 (
    echo.
    echo ======================================================================
    echo [✓] XẾP THỜI KHÓA BIỂU THÀNH CÔNG RỰC RỠ!
    echo Đang tự động mở file Excel kết quả...
    echo ======================================================================
    if exist "Thoi_Khoa_Bieu_Truong_9_Lop.xlsx" (
        start "" "Thoi_Khoa_Bieu_Truong_9_Lop.xlsx"
    )
) else (
    echo.
    echo ======================================================================
    echo [!] QUÁ TRÌNH XẾP LỊCH GẶP SỰ CỐ. Vui lòng kiểm tra lại thông báo ở trên.
    echo ======================================================================
)
echo.
echo Nhấn phím bất kỳ để quay lại menu chính...
pause > nul
goto MENU

:DONG_BO
cls
echo ======================================================================
echo ĐANG ĐỒNG BỘ PHÂN CÔNG TỪ 3 BẢNG NGUỒN VÀO SHEET 'PHAN_CONG'...
echo ======================================================================
echo.
"%PYTHON_CMD%" generate_phan_cong.py
echo.
echo Nhấn phím bất kỳ để quay lại menu chính...
pause > nul
goto MENU

:MO_INPUT
if exist "Input_Mau_TKB.xlsx" (
    echo Đang mở file Input_Mau_TKB.xlsx...
    start "" "Input_Mau_TKB.xlsx"
) else (
    echo [!] Chưa tìm thấy file Input_Mau_TKB.xlsx!
    echo Bạn có thể chọn mục [5] để tạo mới file mẫu.
)
timeout /t 2 > nul
goto MENU

:MO_OUTPUT
if exist "Thoi_Khoa_Bieu_Truong_9_Lop.xlsx" (
    echo Đang mở file Thoi_Khoa_Bieu_Truong_9_Lop.xlsx...
    start "" "Thoi_Khoa_Bieu_Truong_9_Lop.xlsx"
) else (
    echo [!] Chưa có file kết quả. Vui lòng chọn mục [1] để xếp lịch trước.
)
timeout /t 2 > nul
goto MENU

:TAO_MAU
cls
echo ======================================================================
echo KHỞI TẠO FILE EXCEL MẪU 3 BẢNG NGUỒN CHUẨN...
echo ======================================================================
echo.
"%PYTHON_CMD%" generate_phan_cong.py --create-template
echo.
echo Nhấn phím bất kỳ để quay lại menu chính...
pause > nul
goto MENU

:KET_THUC
exit /b 0

