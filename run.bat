@echo off
mode con: cols=68 lines=14
cd /d %~dp0
echo ========================================
echo Formatador de Listas - Flask porta 5442
echo ========================================
if not exist .venv (
    echo Criando ambiente virtual...
    python -m venv .venv
)
call .venv\Scripts\activate
echo Instalando dependencias...
pip install -r requirements.txt
echo Abrindo app em http://127.0.0.1:5442
start http://127.0.0.1:5442
python app.py
pause
