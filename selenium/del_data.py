from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import json

import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# deleted_videos.txtをカンマ区切りでパースし、リスト化

deleted_list = []
with open("deleted_videos.txt", "r", encoding="utf-8") as f:
    line = f.read().strip()
    if line:
        items = [s.strip() for s in line.split(",") if s.strip()]
        for i in range(0, len(items), 3):
            if i+2 < len(items):
                channel = items[i]
                title = items[i+1]
                url = items[i+2]
                deleted_list.append({"channel": channel, "title": title, "url": url})

print("削除済み動画リスト:", deleted_list)


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
for item in deleted_list:
    driver.get(item["url"])
    time.sleep(3)  # 2秒待機
    try:
        xpath = (
            "//button[contains(@class, 'yt-spec-button-shape-next') and "
            "contains(@class, 'icon-button') and "
            "contains(@aria-label, 'その他の操作') and "
            ".//yt-icon]"
        )
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        button = driver.find_element(By.XPATH, xpath)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
        time.sleep(0.5)
        ActionChains(driver).move_to_element(button).click(button).perform()
        print(f"Clicked button for {item['title']}")
    except Exception as e:
        print(f"Button not found or error for {item['title']}: {e}")
    time.sleep(2)
    try:
        save_button = driver.find_element(By.XPATH, "//yt-formatted-string[text()='保存']")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", save_button)
        time.sleep(0.5)
        ActionChains(driver).move_to_element(save_button).click(save_button).perform()
        print(f"Clicked '保存' button for {item['title']}")
    except Exception as e:
        print(f"Could not click '保存' for {item['title']}: {e}")
    time.sleep(1)
    try:
        checkbox = driver.find_element(By.XPATH, "//yt-formatted-string[@id='label' and text()='後で見る']/ancestor::ytd-playlist-add-to-option-renderer//tp-yt-paper-checkbox")
        aria_checked = checkbox.get_attribute("aria-checked")
        if aria_checked == "true":
            driver.execute_script("arguments[0].click();", checkbox)
            print(f"Unchecked '後で見る' for {item['title']}")
        else:
            print(f"'後で見る' already unchecked for {item['title']}")
    except Exception as e:
        print(f"Could not uncheck '後で見る' for {item['title']}: {e}")
    time.sleep(0.5)
    input("Press Enter to continue to the next video...")
