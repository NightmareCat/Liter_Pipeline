@echo off
REM 下载依赖包及其依赖
mkdir packages
pip download -r requirements.txt -d packages

echo 所有包已下载完成
pause
