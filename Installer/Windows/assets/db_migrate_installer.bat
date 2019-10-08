REM @ECHO OFF

REM %~1 to handle the quotes from parameters
set "run_folder=%~1"
set "log=%~2"

(
ECHO "run_folder = %run_folder%"
ECHO "log = %log%"

REM Switch /D - change drive as well if needed
cd /D "%run_folder%"

REM Environment is activated from the script
CALL db_migrate.bat

) >> "%log%" 2>&1