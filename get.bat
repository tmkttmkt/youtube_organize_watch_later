@echo off
REM カレントディレクトリを移動（空白対策含む）
cd /d "C:\TK\newGit\youtube_organize_watch_later"

REM venvを有効化
call "venv\Scripts\activate.bat"

REM ログ出力開始
echo [%date% %time%] スクリプト実行開始 >> log.txt

REM Pythonスクリプト実行
python "selenium\get_data.py" >> log.txt 2>&1

python "score.py" >> log.txt 2>&1

python "tag.py" >> log.txt 2>&1

REM ログ出力終了
echo [%date% %time%] スクリプト完了 >> log.txt
