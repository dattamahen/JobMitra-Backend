@echo off
echo ============================================================
echo   JobMitra Backend - E2E Integration Tests
echo   (Requires backend running on http://localhost:8000)
echo ============================================================
echo.

REM Install dependencies
echo [1/3] Installing test dependencies...
pip install -r requirements_test.txt httpx -q

REM Check server
echo.
echo [2/3] Pre-flight check...
echo   Ensure backend is running: python main.py
echo   Press any key to continue...
pause > nul

REM Run E2E tests
echo.
echo [3/3] Running E2E integration tests...
echo.
python -m pytest tests/e2e/test_api_e2e.py ^
    -v ^
    --tb=short ^
    --html=tests/e2e/reports/e2e_report.html ^
    --self-contained-html ^
    --junitxml=tests/e2e/reports/e2e_junit.xml

echo.
echo ============================================================
echo   REPORTS:
echo     HTML: tests/e2e/reports/e2e_report.html
echo     XML:  tests/e2e/reports/e2e_junit.xml
echo ============================================================
pause
