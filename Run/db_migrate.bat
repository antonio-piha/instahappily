@ECHO OFF
REM We need to be in the database folder where migrations are

cd "..\App\env\Scripts"
CALL activate.bat
cd "..\..\database"

set FLASK_APP=migrator

REM only upgrade should be used from script

REM INIT:
REM flask db init

REM MIGRATE:
REM flask db migrate

REM UPGRADE:
flask db upgrade
