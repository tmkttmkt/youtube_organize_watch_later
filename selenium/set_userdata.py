from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
import undetected_chromedriver as uc
import json
import sys

import shutil
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

def get_exe_dir():
    try:
        if getattr(sys, 'frozen', False):
            # PyInstallerでexe化後の実行時
            return os.path.dirname(sys.executable)
        else:
            # 普通のPythonスクリプト実行時
            return os.path.dirname(os.path.abspath(__file__))
    except AttributeError as e:
        print(f"sys属性エラー: {e}")
        return os.getcwd()  # 現在の作業ディレクトリを返す
    except OSError as e:
        print(f"パス取得エラー: {e}")
        return os.getcwd()  # 現在の作業ディレクトリを返す
    except Exception as e:
        print(f"予期しないエラー: {e}")
        return os.getcwd()  # 現在の作業ディレクトリを返す


# コピー元
source_dir = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data')
current_dir = get_exe_dir()

destination_dir = os.path.join(current_dir, 'User Data')


options = uc.ChromeOptions()
# 必要に応じてプロファイルやその他のオプションを追加
user_data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "User Data"))
profile_dir = "Profile 1"
options.add_argument(f"--user-data-dir={user_data_dir}")
options.add_argument(f"--profile-directory={profile_dir}")


# undetected_chromedriverでブラウザを起動
driver = uc.Chrome(options=options)

print("Chrome browser started with specified profile.")

try:
    driver.get("https://www.youtube.com")

    while True:
        try:
            # 定期的にブラウザにアクセスしてみる
            _ = driver.title
        except WebDriverException:
            print("ブラウザが閉じられました。スクリプトを終了します。")
            break
        time.sleep(1)  # 1秒ごとに監視

finally:
    driver.quit()