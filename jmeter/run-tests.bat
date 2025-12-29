@echo off
REM ===========================================
REM EcoLabel-MS - JMeter Test Runner (Windows)
REM ===========================================

echo ========================================
echo   EcoLabel-MS - JMeter Load Tests
echo ========================================

REM Configuration
set JMETER_HOME=C:\apache-jmeter
set TEST_PLAN=ecolabel-load-test.jmx
set RESULTS_DIR=jmeter-results
set REPORT_DIR=jmeter-report

REM Create directories
if not exist %RESULTS_DIR% mkdir %RESULTS_DIR%
if exist %REPORT_DIR% rmdir /s /q %REPORT_DIR%

REM Get timestamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set TIMESTAMP=%datetime:~0,8%_%datetime:~8,6%

echo.
echo [1/3] Starting services...
docker-compose up -d
timeout /t 30 /nobreak

echo.
echo [2/3] Running JMeter tests...
call %JMETER_HOME%\bin\jmeter.bat -n -t %TEST_PLAN% -l %RESULTS_DIR%\results_%TIMESTAMP%.jtl -e -o %REPORT_DIR%

echo.
echo [3/3] Tests completed!
echo.
echo Results: %RESULTS_DIR%\results_%TIMESTAMP%.jtl
echo Report:  %REPORT_DIR%\index.html
echo.

REM Open report in browser
start "" %REPORT_DIR%\index.html

pause
