@echo off
REM ===== 切换 UTF-8 编码 =====
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ===== 请求管理员权限 =====
net session >nul 2>&1
if %errorlevel% neq 0 (
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

REM --------- 配置项目 ----------
set "PROJECT_NAME=init_spider"

REM --------- 获取绝对路径 ----------
set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..\..\src") do set "SRC_ABS=%%~fI"
for %%I in ("%SCRIPT_DIR%..\..\release") do set "RELEASE_ABS=%%~fI"

REM --------- 打包python 配置 ----------
set "PY_PACKAGE_FILE=%SCRIPT_DIR%package.py"
set "PACKAGE_SRC=%SCRIPT_DIR%src"

REM --------- Node 配置 ----------
set "NODE_EXE=%SRC_ABS%\bin\node.exe"
set "NODE_URL=https://registry.npmmirror.com/-/binary/node/v20.19.5/win-x64/node.exe"

REM --------- uv 配置 ----------
set "UV_EXE=%SRC_ABS%\bin\uv.exe"
set "UV_URL=https://hk.gh-proxy.org/https://github.com/astral-sh/uv/releases/download/0.9.26/uv-x86_64-pc-windows-msvc.zip"
set "UV_ZIP=%SCRIPT_DIR%lib\uv.zip"
set "UV_TMP=%SCRIPT_DIR%lib\uv_tmp"

REM --------- VS配置下载路径 ----------
set "VS_URL=https://aka.ms/vs/17/release/vs_buildtools.exe"
set "VS_EXE=%SCRIPT_DIR%vs_buildtools.exe"

REM --------- WinRAR SC 配置 ----------
set "WINRAR_SC_URL=https://www.win-rar.com/fileadmin/winrar-versions/sc/sc20250804/wrr/winrar-x64-713sc.exe"
set "WINRAR_SC_EXE=%SCRIPT_DIR%lib\WinRAR-7.13-x64-SC.exe"
set "INSTALL_DIR=C:\Program Files\WinRAR"
set "WINRAR_EXE=%INSTALL_DIR%\WinRAR.exe"

REM --------- 配置 MSVC 编译器硬编码路径 ----------
set "VC_VARS_BAT=C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat"

@REM 切换目录
cd %SCRIPT_DIR%

REM --------- 检查 WinRAR SC 文件是否存在 ----------
if not exist "%WINRAR_EXE%" (

    where curl >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo 使用 curl 下载 WinRAR SC.exe...
        curl -L "%WINRAR_SC_URL%" -o "%WINRAR_SC_EXE%" --progress-bar
    )

    if not exist "%WINRAR_SC_EXE%" (
        echo curl 下载失败，尝试 PowerShell 下载 WinRAR SC.exe...
        powershell -Command "Write-Host '正在下载 WinRAR SC.exe...'; Invoke-WebRequest '%WINRAR_SC_URL%' -OutFile '%WINRAR_SC_EXE%'"
    )

    if not exist "%WINRAR_SC_EXE%" (
        echo 错误 WinRAR SC.exe 下载失败
        pause
        exit /b 1
    )

    "%WINRAR_SC_EXE%" /S

    if exist "%WINRAR_SC_EXE%" del "%WINRAR_SC_EXE%"
)

if not exist "%WINRAR_EXE%" (
    echo WinRAR 安装失败
    pause
    exit /b 1
)

REM --------- 获取短路径避免空格 ----------
for %%I in ("%INSTALL_DIR%") do set "SHORTDIR=%%~sI"

REM --------- 下载 VS Build Tools ----------
if not exist "%VC_VARS_BAT%" (

    if exist "%VS_EXE%" del "%VS_EXE%"

    where curl >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo 使用 curl 下载 Visual Studio Build Tools...
        curl -L "%VS_URL%" -o "%VS_EXE%" --progress-bar
    )

    if not exist "%VS_EXE%" (
        echo curl 下载失败，尝试 PowerShell 下载 Visual Studio Build Tools...
        powershell -Command "Write-Host '正在下载 Visual Studio Build Tools...'; Invoke-WebRequest '%VS_URL%' -OutFile '%VS_EXE%'"
    )

    if not exist "%VS_EXE%" (
        echo 错误：下载 VS Build Tools 失败
        exit /b 1
    )

    echo 正在安装 VS Build Tools...

    if not exist "%VS_EXE%" (
        echo 错误：未找到安装程序 "%VS_EXE%"
        pause
        exit /b 1
    )

    "%VS_EXE%" --passive --wait --norestart --nocache ^
               --add Microsoft.VisualStudio.Workload.VCTools ^
               --add Microsoft.VisualStudio.Component.VC.Tools.x86.x64 ^
               --add Microsoft.VisualStudio.Component.Windows11SDK.22621
    
    if exist "%VS_EXE%" del "%VS_EXE%"
)

if exist "%VC_VARS_BAT%" (
    call "%VC_VARS_BAT%" >nul
)

if not exist "%VC_VARS_BAT%" (
    echo Visual Studio Build Tools 安装失败
    pause
    exit /b 1
)

REM --------- 确保 release 文件夹存在 ----------
if not exist "%RELEASE_ABS%" mkdir "%RELEASE_ABS%"

REM --------- 检测源目录 ----------
if not exist "%SRC_ABS%" (
    echo 错误：源目录不存在: "%SRC_ABS%"
    pause
    exit /b 1
)

REM --------- 检查并下载 uv.exe ----------
if not exist "%UV_EXE%" (
    if not exist "%SRC_ABS%\bin" mkdir "%SRC_ABS%\bin"
    if exist "%UV_ZIP%" del "%UV_ZIP%"

    where curl >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo 使用 curl 下载 uv...
        curl -L "%UV_URL%" -o "%UV_ZIP%" --progress-bar
    )

    if not exist "%UV_ZIP%" (
        echo curl 下载失败，尝试 PowerShell 下载 uv...
        powershell -Command "Write-Host '正在下载 uv...'; Invoke-WebRequest '%UV_URL%' -OutFile '%UV_ZIP%'"
    )

    if not exist "%UV_ZIP%" (
        echo 错误 uv 下载失败
        pause
        exit /b 1
    )

    if exist "%UV_TMP%" rd /s /q "%UV_TMP%"
    mkdir "%UV_TMP%"
    "%WINRAR_EXE%" x -inul -ibck -y "%UV_ZIP%" "%UV_TMP%\"

    set "FOUND_UV="
    for /r "%UV_TMP%" %%F in (uv.exe) do (
        copy /y "%%F" "%UV_EXE%" >nul
        set "FOUND_UV=1"
        goto :UV_DONE
    )
    :UV_DONE
    if exist "%UV_TMP%" rd /s /q "%UV_TMP%"
    if exist "%UV_ZIP%" del "%UV_ZIP%"
    if not exist "%UV_EXE%"  (
        echo 错误 uv.exe 解压失败
        pause
        exit /b 1
    )
)

REM --------- 检查并下载 node.exe ----------
if not exist "%NODE_EXE%" (
    if not exist "%SRC_ABS%\bin" mkdir "%SRC_ABS%\bin"

    where curl >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo 使用 curl 下载 node.exe...
        curl -L "%NODE_URL%" -o "%NODE_EXE%" --progress-bar
    )

    if not exist "%NODE_EXE%" (
        echo curl 下载失败，尝试 PowerShell 下载 node.exe...
        powershell -Command "Write-Host '正在下载 node.exe...'; Invoke-WebRequest '%NODE_URL%' -OutFile '%NODE_EXE%'"
    )

    if not exist "%NODE_EXE%" (
        echo 错误 node.exe 下载失败
        pause
        exit /b 1
    )
)

REM --------- 初始化uv环境 ----------
if exist "%PACKAGE_SRC%" rmdir /s /q "%PACKAGE_SRC%"
%UV_EXE% sync
%UV_EXE% add pathspec
%UV_EXE% run %PY_PACKAGE_FILE%

REM --------- 检测打包目录 ----------
if not exist "%PACKAGE_SRC%" (
    echo 错误：打包目录不存在: "%PACKAGE_SRC%"
    pause
    exit /b 1
)

REM --------- 打包生成自解压 EXE ----------
set "EXE_NAME=%PROJECT_NAME%.exe"
set "EXE_ABS=%RELEASE_ABS%\%EXE_NAME%"

if exist "%EXE_ABS%" del "%EXE_ABS%"
echo WinRAR 正在打包

"%WINRAR_EXE%" a ^
    -r ^
    -ep1 ^
    -sfx ^
    -inul ^
    -ibck ^
    -z"%SCRIPT_DIR%lib\sfx.txt" ^
    -m5 ^
    -x@"%SCRIPT_DIR%lib\exclude.txt" ^
    "%EXE_ABS%" ^
    "%PACKAGE_SRC%\*"

if %ERRORLEVEL% NEQ 0 (
    echo WinRAR 打包失败
    pause
    exit /b 1
)

echo.
echo ===== 打包完成 =====
echo 最终 exe 绝对路径: "%EXE_ABS%"
pause
endlocal
