@echo off
"C:\Users\MINEDUCYT\OneDrive\Desktop\gemini\.venv\Scripts\python.exe" -c "import ast,sys; ast.parse(open('main.py').read()); print('SYNTAX OK')" > _syntax.txt 2>&1
echo done >> _syntax.txt