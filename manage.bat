@echo off
chcp 65001 >nul
setlocal

set BACKEND_PORT=8686
set FRONTEND_PORT=5173

if "%1"=="" goto :usage
if /i "%1"=="start" goto :start
if /i "%1"=="stop" goto :stop
if /i "%1"=="restart" goto :restart
if /i "%1"=="status" goto :status
goto :usage

:usage
echo ========================================
echo Software Guard 服务管理脚本
echo ========================================
echo 用法: manage.bat [命令]
echo.
echo 命令:
echo   start   - 启动前后端服务
echo   stop    - 关闭前后端服务
echo   restart - 重启前后端服务
echo   status  - 查看服务状态
echo ========================================
goto :end

:start
echo.
echo [启动服务]
echo.
cd /d "%~dp0backend"
echo 启动后端服务 (端口 %BACKEND_PORT%)...
start "Software Guard Backend" cmd /k "uv run python main.py"
timeout /t 2 /nobreak >nul

cd /d "%~dp0frontend"
echo 启动前端服务 (端口 %FRONTEND_PORT%)...
start "Software Guard Frontend" cmd /k "pnpm dev"

echo.
echo ✓ 服务启动完成
goto :end

:stop
echo.
echo [关闭服务]
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%BACKEND_PORT%.*LISTENING"') do (
    if not "%%a"=="" (
        echo 正在关闭后端进程 (PID: %%a)...
        taskkill /PID %%a /F >nul 2>&1
    )
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%FRONTEND_PORT%.*LISTENING"') do (
    if not "%%a"=="" (
        echo 正在关闭前端进程 (PID: %%a)...
        taskkill /PID %%a /F >nul 2>&1
    )
)

echo.
echo ✓ 服务已关闭
goto :end

:restart
call :stop
timeout /t 2 /nobreak >nul
call :start
goto :end

:status
echo.
echo [服务状态]
echo.

set BACKEND_RUNNING=0
set FRONTEND_RUNNING=0

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%BACKEND_PORT%.*LISTENING"') do (
    if not "%%a"=="" (
        set BACKEND_RUNNING=1
        echo 后端服务: 运行中 (PID: %%a, 端口: %BACKEND_PORT%)
    )
)

for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%FRONTEND_PORT%.*LISTENING"') do (
    if not "%%a"=="" (
        set FRONTEND_RUNNING=1
        echo 前端服务: 运行中 (PID: %%a, 端口: %FRONTEND_PORT%)
    )
)

if %BACKEND_RUNNING%==0 echo 后端服务: 未运行
if %FRONTEND_RUNNING%==0 echo 前端服务: 未运行
echo.
goto :end

:end
endlocal
