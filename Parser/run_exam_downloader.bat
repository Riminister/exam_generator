@echo off
echo Activating Queen's Exam Bank Environment...
call queens_exam_env\Scripts\activate.bat
echo Environment activated!
echo.
echo Running Queen's Exam Bank Downloader...
python parse.py
pause
