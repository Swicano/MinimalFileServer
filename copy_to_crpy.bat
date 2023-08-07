@echo off
set source=C:\Users\fires\Projects\ESP32_S3\circuitpython\MinimalFileServer\Code
set destination=E:

xcopy /D /Y /I /S /E "%source%\*" "%destination%"
pause
