@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
set "YZM_PYTHON=%LocalAppData%\Programs\Python\Python310\python.exe"
if exist "%YZM_PYTHON%" goto localpython
py -3 deney.py
if errorlevel 1 goto failed
py -3 dogrula.py
if errorlevel 1 goto failed
goto success
:localpython
"%YZM_PYTHON%" deney.py
if errorlevel 1 goto failed
"%YZM_PYTHON%" dogrula.py
if errorlevel 1 goto failed
:success
echo Deney ve dogrulama tamamlandi. Rapor output\pdf klasorundedir.
pause
exit /b 0
:failed
echo Islem tamamlanamadi. Python ve requirements.txt paketlerini kontrol edin.
pause
exit /b 1
