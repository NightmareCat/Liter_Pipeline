@echo off

echo 正在安装本地依赖包...
pip install --no-index --find-links=packages -r requirements.txt

echo 离线安装完成，已部署 Python 和所需依赖。
pause
