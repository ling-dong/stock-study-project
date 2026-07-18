@echo off
chcp 65001 >nul

cd /d "%~dp0"

if not exist scripts\stop_all.py (
    echo [ERROR] scripts\stop_all.py 不存在
    pause
    exit /b 1
)

echo.
echo  ============================================
echo   SPAS + Investment Academy 一键关闭
echo  ============================================
echo.

python scripts\stop_all.py --force

echo.
echo 按任意键退出...
pause >nul
