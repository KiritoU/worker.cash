winget install --id Git.Git -e --source winget
winget install -e --id Python.Python.3.10 --scope machine

@echo off
set "PATH=%PATH%;C:\Program Files\Git\bin;C:\Program Files\Python310"

set username=%USERNAME%
cd C:\Users\%username%\Desktop

git clone https://github.com/KiritoU/worker.cash.git
cd worker.cash

python -m venv venv
call .\venv\Scripts\activate
pip install -r requirements.txt

pause
