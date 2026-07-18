@echo off
chcp 65001 >nul

cd /d "%~dp0"

if not exist scripts\start_all.py (
    echo [ERROR] scripts\start_all.py 不存在
    pause
    exit /b 1
)

echo.
echo  ============================================
echo   SPAS + Investment Academy 一键启动
echo  ============================================
echo.

python scripts\start_all.py %*

if errorlevel 1 (
    echo.
    echo [ERROR] 启动失败
    pause
)
