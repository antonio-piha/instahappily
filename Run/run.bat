REM We need to be in the App folder where environment is

cd "..\App\env\Scripts"
CALL activate.bat
cd "..\..\"

set FLASK_APP=app
set FLASK_ENV=production
set FLASK_RUN_PORT=5555
set FLASK_RUN_HOST=0.0.0.0

flask run
