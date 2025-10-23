@echo off
echo ========================================
echo Queen's Exam Bank Downloader Environment
echo ========================================
echo.
echo Activating virtual environment...
call queens_exam_env\Scripts\activate.bat
echo.
echo Environment ready! You can now run:
echo   python parse.py
echo.
echo Or use the batch file: run_exam_downloader.bat
echo.
cmd /k
