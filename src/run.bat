@echo off

REM cd 到 bat 所在目录（SFX 解压后的目录）
cd /d %~dp0

@REM 设置当前目录环境
set PATH=%~dp0bin;%PATH%

@REM Python环境
uv sync
uv run main.py

pause
