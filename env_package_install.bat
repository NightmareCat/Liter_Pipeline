@echo off
REM ���õ�ǰĿ¼Ϊ�ű�����Ŀ¼
cd /d %~dp0

REM 2. ���� pip ·��
set PATH=C:\Python310\Scripts;C:\Python310;%PATH%

REM 3. ��װ����������
echo ���ڰ�װ����������...
pip install --no-index --find-links=packages -r requirements.txt

echo ���߰�װ��ɣ��Ѳ��� Python ������������
pause
