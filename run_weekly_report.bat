@echo off
REM Weekly Report Task
REM Run this batch file from Task Scheduler

REM Set the working directory
cd /d "C:\Users\Keerti A M\Documents\rcs_projects\rcs_rest\whatsapp_saas"

REM Run the Django command with absolute path to Python
"C:\Users\Keerti A M\Documents\rcs_projects\rcs_rest\venv\Scripts\python.exe" manage.py weekly_report

REM Log the execution (optional - helps with debugging)
echo Weekly report executed at %date% %time% >> "C:\Users\Keerti A M\Documents\rcs_projects\rcs_rest\task_log.txt"
