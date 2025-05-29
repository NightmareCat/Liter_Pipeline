@echo off
REM 设置当前目录为脚本所在目录
cd /d %~dp0

REM 2. 设置 pip 路径
set PATH=C:\Python310\Scripts;C:\Python310;%PATH%

REM 3. 安装本地依赖包
echo 正在安装本地依赖包...
pip install --no-index --find-links=packages -r requirements.txt

echo 离线安装完成，已部署 Python 和所需依赖。
pause
