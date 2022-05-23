@echo off
set "FLASK_ENV=development"
start chrome http://127.0.0.1:5000/
python run.py
pause