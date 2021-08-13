@echo off 
echo Starting project!
set FLASK_APP=fkstreaming
set FLASK_ENV=development
flask run --host=0.0.0.0
pause