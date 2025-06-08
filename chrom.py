from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import json

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

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
time.sleep(2)  # 2秒待機
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
def parse_views(views_str):
    # 例: "2.8万 回視聴" → 28000, "1234 回視聴" → 1234, "1.2億 回視聴" → 120000000
    s = views_str.replace(',', '').split(' ')[0]
    num = 0
    if '億' in s:
        num = float(s.replace('億', '')) * 100000000
    elif '万' in s:
        num = float(s.replace('万', '')) * 10000
    else:
        try:
            num = float(s)
        except ValueError:
            num = 0
    return int(num)
# 「後で見る」の動画リストを取得
videos = driver.find_elements(By.XPATH, "//ytd-playlist-video-renderer")
video_data = []
for video in videos:
    try:
        title_elem = video.find_element(By.CSS_SELECTOR, "#video-title")
        channel_elem = video.find_element(By.CSS_SELECTOR, "a.yt-simple-endpoint.style-scope.yt-formatted-string")
        length_elem = video.find_element(By.CSS_SELECTOR, "span.ytd-thumbnail-overlay-time-status-renderer")
        print(":",length_elem.text)
        metadata_spans = video.find_elements(By.CSS_SELECTOR, "span.style-scope.yt-formatted-string")
        views = metadata_spans[0].text.strip() if len(metadata_spans) > 0 else ""
        published = metadata_spans[2].text.strip() if len(metadata_spans) > 2 else ""
        title = title_elem.text.strip() if title_elem else ""
        channel = channel_elem.text.strip() if channel_elem else ""
        length = length_elem.get_attribute("aria-label") if length_elem else ""
        # もしaria-labelがなければテキストを使う
        if not length:
            length = length_elem.text.strip() if length_elem else ""
        insert_date = time.strftime("%Y-%m-%d")
        video_data.append({
            "title": title,
            "channel": channel,
            "length": length,
            "published": published,
            "views": parse_views(views),
            "insert": insert_date
        })
    except Exception as e:
        print(f"動画情報の取得に失敗: {e}")

# JSONファイルに書き込む
with open("watch_later.json", "w", encoding="utf-8") as f:
    json.dump(video_data, f, ensure_ascii=False, indent=2)

print("動画情報をwatch_later.jsonに保存しました。")

time.sleep(2)  # 2秒待機
# ブラウザを閉じる
driver.quit()