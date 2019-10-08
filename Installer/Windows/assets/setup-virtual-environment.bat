REM @ECHO OFF

REM %~1 to handle the quotes from parameters
set "app_folder=%~1"
set "log=%~2"

(
ECHO "app_folder = %app_folder%"
ECHO "log = %log%"

REM Switch /D - change drive as well if needed
cd /D "%app_folder%"

REM Make sure we have pip
py -3.6 -m pip install -U pip

REM Activate virtual environment
REm Tested - works when virtual environment already exists
py -3.6 -m venv env
cd "env\Scripts"
CALL activate.bat
cd "..\.."

REM Pip ugrade, make sure on latest version
REM This is needed because venv can get old version
python -m pip install -U setuptools
python -m pip install -U pip

REM Install requirements
pip install -r requirements.txt
pip install -U -r requirements.txt

) >> "%log%" 2>&1
