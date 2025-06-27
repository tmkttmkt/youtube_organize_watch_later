from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import json
import sys

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

# コマンドライン引数からソート方法を取得
sort_method = "date_asc"  # デフォルト値
if len(sys.argv) > 1:
    sort_method = sys.argv[1]

print(f"ソート方法: {sort_method}")

# オプションの設定
options = uc.ChromeOptions()
# 必要に応じてプロファイルやその他のオプションを追加
user_data_dir = os.path.expandvars(r"C:\User Data")
profile_dir = "Profile 1"
options.add_argument(f"--user-data-dir={user_data_dir}")
options.add_argument(f"--profile-directory={profile_dir}")


# undetected_chromedriverでブラウザを起動
driver = uc.Chrome(options=options)

print("Chrome browser started with specified profile.")
time.sleep(2)  # 2秒待機

# YouTubeを開く
driver.get("https://www.youtube.com")
time.sleep(6)  # 2秒待機
# ログインボタンがあったらログインする
try:
    login_button = driver.find_element(By.XPATH, "//yt-formatted-string[text()='ログイン']")
    login_button.click()
    time.sleep(2)  # 2秒待機
    # アカウント名を変数化
    account_name_text = "レーニンの演説聞く人は零人"  # ここにクリックしたいアカウント名を入力
    # アカウント選択画面でアカウント名をクリック
    account_name = driver.find_element(By.XPATH, f"//div[@data-identifier and .='{account_name_text}']")
    account_name.click()
except Exception as e:
    print("ログインボタンが見つかりませんでした。スキップします。")
time.sleep(3)

# 「後で見る」をクリック
try:
    watch_later_button = driver.find_element(By.XPATH, "//yt-formatted-string[text()='後で見る']")
    watch_later_button.click()
    print("「後で見る」をクリックしました。")
except Exception as e:
    print("「後で見る」ボタンが見つかりませんでした。")

time.sleep(2)  # 2秒待機

# 一番下までスクロール
last_height = driver.execute_script("return document.documentElement.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
    time.sleep(2)
    new_height = driver.execute_script("return document.documentElement.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height
print("一番下までスクロールしました。")

driver.execute_script("window.scrollTo(0, 0);")
print("一番上に戻りました。")

input("ブラウザが起動しました。Enterキーを押して続行してください...")