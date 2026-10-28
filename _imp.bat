@echo off
.venv\Scripts\python.exe -c "import main; print('IMPORT_OK')" > _imp.txt 2>&1
echo EXIT=%ERRORLEVEL% >> _imp.txt