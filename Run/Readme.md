## PREPARE YOUR DEV ENVIRONMENT

Requirements:
PyInstaller==3.4
pypiwin32
python C:\Program Files\Python36\Scripts\pywin32_postinstall.py -install



## TO BUILD THE SERVICE.EXE
pyinstaller --onefile --distpath . --log-level ERROR -F --hidden-import win32timezone -i ..\Installer\assets\images\logo.ico InstaHappilyService.py


Run
(env) dist\WindowsService.exe --startup auto install
Installing service TestService
Service installed

(env) dist\WindowsService.exe start
Starting service TestService


Clean
(env) dist\WindowsService.exe stop
(env) dist\WindowsService.exe remove
