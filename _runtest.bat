@echo off
.venv\Scripts\python.exe _test_harness.py > _test_result.txt 2>&1
echo EXITCODE=%ERRORLEVEL% >> _test_result.txt