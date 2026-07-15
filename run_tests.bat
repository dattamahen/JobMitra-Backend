@echo off
echo ============================================
echo   JobMitra Backend - Test Suite Runner
echo ============================================
echo.

REM Install test dependencies
echo [1/3] Installing test dependencies...
pip install -r requirements_test.txt -q

REM Run tests with coverage and HTML report
echo.
echo [2/3] Running test suite...
echo.
python -m pytest tests/ ^
    -v ^
    --tb=short ^
    --html=tests/reports/test_report.html ^
    --self-contained-html ^
    --junitxml=tests/reports/junit_report.xml ^
    --cov=. ^
    --cov-report=html:tests/reports/coverage_html ^
    --cov-report=term-missing ^
    --cov-config=.coveragerc ^
    -x

echo.
echo [3/3] Test execution complete!
echo.
echo Reports generated:
echo   - HTML Report: tests/reports/test_report.html
echo   - JUnit XML:   tests/reports/junit_report.xml
echo   - Coverage:    tests/reports/coverage_html/index.html
echo.
echo ============================================
pause
