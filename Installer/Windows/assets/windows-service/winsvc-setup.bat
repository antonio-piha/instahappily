set app_folder=%1
set log=%2

REM (
ECHO "app_folder = " + %app_folder%
ECHO "log = " + %log%

REM Install as service

REM Switch /D - change drive as well if needed
set run_folder=%app_folder% + "\Run"

REM Set service as startup Automatic then start
START /D "%run_folder%" /WAIT InstaHappilyService.exe --startup auto install
START /D "%run_folder%" /WAIT InstaHappilyService.exe start

REM ) >> "%log%" 2>&1