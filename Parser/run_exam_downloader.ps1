# PowerShell script to run Queen's Exam Bank Downloader
Write-Host "Activating Queen's Exam Bank Environment..." -ForegroundColor Green
& ".\queens_exam_env\Scripts\Activate.ps1"
Write-Host "Environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "Running Queen's Exam Bank Downloader..." -ForegroundColor Cyan
python parse.py
Read-Host "Press Enter to exit"
